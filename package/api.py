import psycopg2
from psycopg2.errorcodes import UNIQUE_VIOLATION
from psycopg2 import errors
import pandas as pd
import sys
import traceback
import numpy as np
try:
    import package.utils as utils
except:
    import utils
from tqdm import tqdm

class DB:
    """database interface class"""

    @staticmethod
    def connect(params: dict) -> [psycopg2.extensions.connection, psycopg2.extensions.cursor]:
        """
            @brief: connects to the database
            @params:
                params: dictionary of db connection parameters
            @returns:
                db: the database
                cur: the cursor
        """

        try:
            print("[INFO] connecting to db.")
            db = psycopg2.connect(**params)
            print("[INFO] connected.")
            cur = db.cursor()
        except Exception as e:
            print("[ERROR] failed to connect to db.")
            print(e)
            return []
        return [db, cur]

    @staticmethod
    def execute(sql_query: str, database: psycopg2.extensions.connection) -> pd.DataFrame:
        """
            @brief: shorthand sql style execution, preferred method for select statements
            @params:
                sql_query: the query string to execute
                database: the database to execute on
            @returns: a pandas table of the query results
        """
        try:
            return pd.read_sql_query(sql_query, database)
        except Exception as e:
            print(e)
            print(traceback.print_exc())
            if ('NoneType' in str(e)):
                print("ignoring error")
            return pd.DataFrame()

    @staticmethod
    def get_tables(db: psycopg2.extensions.connection) -> pd.DataFrame:
        """Returns a DataFrame of the tables in a given database"""
        return DB.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""", db)



    @staticmethod
    def table_exists(tb: str = '',
                     db: psycopg2.extensions.connection = None) -> bool:
        res = DB.execute(f"""select * from information_schema.tables where table_schema = 'public' and table_name = '{tb}';""", db)
        if len(res.table_name.values) > 0:
            return True
        else:
            return False



    @staticmethod
    def get_fields(tb: str = None,
                   as_list: bool = True,
                   db: psycopg2.extensions.connection = None) -> pd.DataFrame or list:
        """Returns the fields (column headers) for a given table"""

        assert tb is not None and db is not None, '[ERROR] must supply the name of the table (tb=__) and psycopg2.extensions.connection (db=__)'

        res = DB.execute("""SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '{}';""".format(tb), db)
        if not as_list:
            return res
        else:
            return [col for cols in res.values.tolist() for col in cols]




    @staticmethod
    def batch_insert(df: pd.DataFrame = None,
                     tb: str = '',
                     num_batches: int = 10,
                     db: psycopg2.extensions.connection = None,
                     cur: psycopg2.extensions.cursor = None,
                     verbose: bool = False) -> int:
        """
        returns the id of the last record inserted
        """
        assert tb in DB.get_tables(db).values, f'[ERROR] table <{tb}> does not exist'
        assert all(col in DB.get_fields(f'{tb}', as_list=True, db=db) for col in list(df.columns)), f'[ERROR] target table <{tb}> does not contain all passed columns <{list(df.columns)}>'
        # about 100x faster than a for loop, 2x faster than using executemany or execute_batch
        # uses a generator to bypass memory issues
        values = list(tuple(x) for x in zip(*(df[x].values.tolist() for x in list(df.columns))))
        
        chunk_size = int(len(values)/num_batches)
        if chunk_size == 0:
            chunk_size = len(values)

        if verbose:
            print(f'chunk size: {chunk_size}, values shape: {len(values)}, {len(values[0])}')
            
        for i, chunk in utils.chunk_generator(values, chunk_size):
            vals = str(chunk).replace('[', '').replace(']', '')
            statement = f"""INSERT INTO {tb} {str(tuple(df.columns)).replace("'", '"')} VALUES {vals};"""
            try:
                cur.execute(statement)
                db.commit()
            except Exception as e:
                # get error code
                print(str(e))
                
                db.rollback()
        return DB.execute(f"select max(id) from {tb};", db).values[0][0]




    @staticmethod
    def _create_asset_type(asset_type: str = None,
                           subtype: str = None,
                           description: str = None,
                           db: psycopg2.extensions.connection = None,
                           cur: psycopg2.extensions.cursor = None) -> pd.DataFrame:
        """
        returns the asset type as a dataframe
        """
        assert asset_type is not None and subtype is not None, "[ERROR] must supply <asset_type>(str) and <subtype>(str)."

        try:
            if description is not None:
                cur.execute(f"""INSERT INTO asset_type_tb ("type", "subtype","description") values ('{asset_type}', '{subtype}', '{description}');""")
            else:
                cur.execute(f"""INSERT INTO asset_type_tb ("type", "subtype") values ('{asset_type}', '{subtype}');""")
            db.commit()
        except psycopg2.errors.UniqueViolation:
            print("[INFO] asset_type already exists.")
        asset_type_df = DB._get_asset_type(asset_type=asset_type, subtype=subtype, id_only=False, db=db)

        return asset_type_df




    @staticmethod
    def _get_asset_type(asset_type: str = None,
                        subtype: str = None,
                        type_id: int = None,
                        id_only: bool = True,
                        db: psycopg2.extensions.connection = None) -> int:
        """
        returns the asset type id or the asset type as dataframe
        """
        assert type_id or (asset_type is not None and subtype is not None) is not None, "[ERROR] must supply <asset_type>(str) and <subtype>(str), or <type_id>(int)."
        try:
            if type_id is not None:
                id_only = False
                statement = f"""select * from asset_type_tb where "id" = {type_id}"""
            else:
                statement = f"""select * from asset_type_tb where "type" ilike '%{asset_type}%' and "subtype" ilike '%{subtype}%';"""

            res = DB.execute(statement, db)
            if id_only:
                return int(res.id.values[0])
            else:
                return res
        except IndexError:
            print("[ERROR] asset_type does not exist or invalid parameters passed")
            return -1



    @staticmethod
    def _create_asset(type_id: int = None,
                      owner: str = '',
                      process_id: int = None,
                      group_id: int = None,
                      serial_number: str = '',
                      common_name: str = '',
                      age: float = None,
                      eol: float = None,
                      rul: float = None,
                      units: str = None,
                      db: psycopg2.extensions.connection = None,
                      cur: psycopg2.extensions.cursor = None,
                      sandbox=False):
        """
        flexible function to create asset based on any combination of required and optional parameters
        owner, serial_number, and age have default db values so they can be ignored if desired
        process_id, common_name, eol, rul, and units are not required
        """
        assert type_id is not None and type(type_id) == int, '[ERROR] must supply <type_id>(int)'
        statement = 'insert into asset_tb("type_id", "group_id"'
        values = [type_id, group_id]
        if len(owner) > 2:
            statement = statement + ',"owner"'
            values.append(owner)
        if process_id is not None and type(process_id) == int:
            statement = statement + ',"process_id"'
            values.append(process_id)
        if len(serial_number) > 2:
            statement = statement + ',"serial_number"'
            values.append(serial_number)
        if len(common_name) > 2:
            statement = statement + ',"common_name"'
            values.append(common_name)
        if age is not None and type(age) == float:
            statement = statement + ',"age"'
            values.append(age)
        if eol is not None and type(eol) == float:
            statement = statement + ',"eol"'
            values.append(eol)
        if rul is not None and type(rul) == float:
            statement = statement + ',"rul"'
            values.append(rul)
        if units is not None:
            statement = statement + ',"units"'
            values.append(units)
        if len(values) == 1:
            print('here')
            statement = statement + f""") values ({values[0]});"""
        else:
            statement = statement + f""") values {tuple(values)};"""
        if sandbox:
            print(statement)
            return statement
        else:
            try:
                res = DB._get_asset(serial_number=serial_number, db=db)
                if len(res) > 0:
                    return res
                else:
                    cur.execute(statement)
                    db.commit()
            except psycopg2.errors.UniqueViolation:
                print("[ERROR] asset already exists (serial numbers must be unique).")
            return DB._get_asset(serial_number=serial_number, db=db)



    @staticmethod
    def get_devices(db):
        query = "select ast.*, irt.unit from asset_tb ast join irel_transistor_tb irt on ast.id = irt.id;"
        res1 = DB.execute(query, db)

        query = "select ast.*, cbt.unit from asset_tb ast join cooling_block_tb cbt on ast.id = cbt.id;"
        res2 = DB.execute(query, db)

        return pd.concat([res1, res2])
    
    
    
    @staticmethod
    def get_rounds(db):
        query = "select * from group_tb;"
        return DB.execute(query, db)
    
    
    
    @staticmethod
    def get_device_data(unit, db):
        query = f"""
            select dtt."asset_id", 
                   dtt."group_id",
                   dtt."dt", 
                   dtt."cycle", 
                   dtt."temperature", 
                   dtt."status",
                   dtt."voltage", 
                   gtt."current" 
            from data_tb dtt 
            join group_tb gtt on dtt.group_id = gtt.id
            where dtt.asset_id = {unit} order by dtt."dt";
        """
        print(f"getting data for asset {unit}")
        df = DB.execute(query, db)
        print(f"processing asset {unit}")
        df.sort_values(by=['asset_id', 'dt', 'cycle'], inplace=True)
        df.index = df['dt']
        df.drop(columns=['dt'], inplace=True)
        df.asset_id = df.asset_id.astype(np.int16)
        df.cycle = df.cycle.astype(np.int32)
        df.temperature = df.temperature.astype(np.float32)
        df.voltage = df.voltage.astype(np.float32)
        df.loc[df.status == 0, 'voltage'] = 0
        
        return df
        
        print(f"creating cycle pos column for asset {asset_id}")
        new_df = pd.DataFrame()
        for group in pd.unique(df.current):
            group_df = df[df['current'] == group]
            for asset in pd.unique(group_df.asset_id):
                _df = pd.DataFrame()
                #print(group, asset)
                _df = group_df[group_df['asset_id'] == asset]
                _df = _df.resample('1s').mean().dropna()
                _df.cycle = _df.cycle.apply(np.round)
                _df['cycle_pos'] = 0
                for cycle in pd.unique(_df.cycle):
                    num_samples = len(_df[_df.cycle == cycle])
                    _df.loc[_df.cycle == cycle, 'cycle_pos'] = np.arange(0, num_samples)/num_samples
                new_df = new_df.append(_df)

        return new_df

    
    
    
    @staticmethod
    def get_unit_stats(unit, downsample, voltage_cutoff, db):
        query = f"""select asset_id, "cycle",
                round(avg(voltage)::numeric, 2) as "mean_voltage",
                round(avg(temperature)::numeric, 2) as "mean_temperature",
                round(stddev(voltage)::numeric,2) as "std_voltage",
                round(stddev(temperature)::numeric,2) as "std_temperature",
                round(min(voltage)::numeric,2) as "min_voltage",
                round(min(temperature)::numeric,2) as "min_temperature",
                round(max(voltage)::numeric,2) as "max_voltage",
                round(max(temperature)::numeric,2) as "max_temperature"
                from data_tb
                where voltage > {voltage_cutoff}
                and asset_id = {unit} """
        if downsample > 1:
            query = query + f"""and "cycle" % {downsample} = 0 """
        query = query + """group by ("cycle", "asset_id") order by ("cycle", "asset_id");"""
        df = DB.execute(query, db)
        return df

    
    
    
    
    def get_round_data(group_id, db, include_cooling_block=False):
        group_id = 2
        query1 = f"""select * from data_tb where group_id = {group_id} order by (asset_id, dt);"""
        res1 = DB.execute(query1, db)
        
        if include_cooling_block:
            query2 = f"""select * from cb_data_tb where group_id = {group_id};"""
            res2 = DB.execute(query2, db)
            return res1, res2
        else:
            return res1
    
    
    
    
    
    
        
    @staticmethod
    def _get_asset(serial_number: str = None,
                   id: int = None,
                   db: psycopg2.extensions.connection = None):
        """
        returns the asset as a dataframe
        """
        assert serial_number is not None or id is not None, '[ERROR] must supply <serial_number>(str) or <id>(int)'
        assert db is not None, '[ERROR] must pass <db>(psycopg2.extensions.connection)'
        if serial_number is not None:
            statement = f"""select * from asset_tb where "serial_number" = '{serial_number}';"""
        else:
            statement = f"""select * from asset_tb where "id" = {id};"""
        return DB.execute(statement, db)



    @staticmethod
    def _create_component(asset: pd.DataFrame = None,
                          unit: int = None,
                          num_samples: int = None,
                          manufacturer: str = None,
                          misc_info: str = None,
                          db: psycopg2.extensions.connection = None,
                          cur: psycopg2.extensions.cursor = None):
        """
        creates a component in the db, the asset must be created first
        """
        assert asset is not None and unit is not None, '[ERROR] must supply all parameters'
        asset_type = DB._get_asset_type(type_id=asset.type_id.values[0], db=db)
        assert len(asset_type) > 0, f'[ERROR] a valid asset type was not found with id <{asset.type_id.values[0]}>'

        table_name = f"{asset_type.type.values[0]}_{asset_type.subtype.values[0]}_tb"
        assert DB.table_exists(table_name, db), f'[ERROR] table <{table_name}> does not exist'
        if num_samples == None and misc_info == None:
            statement = f"""insert into {table_name}("id", "unit") values ({asset.id.values[0]}, {unit});"""
        else:
            statement = f"""insert into {table_name}("id", "unit", "num_samples", "misc_info") values ({asset.id.values[0]}, {unit}, {num_samples}, '{misc_info}');"""
        try:
            cur.execute(statement)
            db.commit()
        except Exception as e:
            print(e)

        return DB.execute(f"""select * from {table_name} where "id" = {asset.id.values[0]}""", db)



    @staticmethod
    def _get_units(group_id: [] = None,
                   Fc: [] = None,
                   datasets: [] = None,
                   order_by: str = 'id',
                   db: psycopg2.extensions.connection = None):
        valid_order_by = [
            'id',
            'age',
            'rul'
        ]
        statement = """select ast."id", 
        ast."serial_number", 
        ast."age", 
        ast."eol",  
        ast."rul", 
        ent."group_id", 
        ent."Fc", 
        ent."unit", 
        ent."dataset" 
        from asset_tb ast 
        join engine_ncmapss_tb ent 
        on ast.id = ent.id """
        assert isinstance(group_id, list) or isinstance(group_id, type(None)), '[ERROR] pass arguments as lists'
        assert isinstance(Fc, list) or isinstance(Fc, type(None)), '[ERROR] pass arguments as lists'
        assert isinstance(datasets, list) or isinstance(datasets, type(None)), '[ERROR] pass dataset as a list'
        assert order_by in valid_order_by, f'[ERROR] <order_by> bust be in {valid_order_by}'

        if group_id is not None:
            if len(group_id) > 1:
                group_id = tuple(group_id)
            elif len(group_id) == 1:
                group_id = f'({group_id[0]})'

        if Fc is not None:
            if len(Fc) > 1:
                Fc = tuple(Fc)
            elif len(Fc) == 1:
                Fc = f'({Fc[0]})'

        if datasets is not None:
            if datasets[0] == 'all':
                datasets = tuple(valid_datasets)
            elif len(datasets) > 1:
                datasets = tuple(datasets)
            elif len(datasets) == 1:
                datasets = f"('{datasets[0]}')"

        clause = ''
        if group_id is not None:
            clause = f'where ent."group_id" in {group_id} '

        if Fc is not None:
            if group_id is not None:
                clause = clause + f'and ent."Fc" in {Fc} '
            else:
                clause = f'where ent."Fc" in {Fc} '

        if datasets is not None:
            if isinstance(datasets, tuple):
                for ds in datasets:
                    assert (any(ds in sub for sub in valid_datasets)), f'[ERROR] valid dataset was not supplied. valid datasets are {valid_datasets}'
            elif isinstance(datasets, str):
                assert eval(datasets) in valid_datasets, f'[ERROR] valid dataset was not supplied. valid datasets are {valid_datasets}'
            if group_id is not None or Fc is not None:
                clause = clause + f'and ent."dataset" in {datasets} '
            else:
                clause = f'where ent."dataset" in {datasets} '

        statement = statement + clause
        statement = statement + f'order by ast."{order_by}" asc;'

        return DB.execute(statement, db)






    @staticmethod
    def _get_data(units: [] = None,
                  limit: int = None,
                  table: str = None,
                  date_start: str = None,
                  date_stop: str = None,
                  cycle_start: int = None,
                  cycle_stop: int = None,
                  drop_cols: [] = None,
                  db: psycopg2.extensions.connection = None) -> pd.DataFrame:
        valid_units = DB.execute("select id from asset_tb;", db).values

        assert units is None or all(unit in valid_units for unit in units), '[ERROR], either do not pass a value for <units> or ensure all values passed are valid'


        statement = f"""select * from {table} where asset_id = {units[0]} order by id asc;"""
        if drop_cols is None:
            return DB.execute(statement, db)
        else:
            return DB.execute(statement, db).drop(columns=drop_cols)



    def _create_group(group: str = None,
                      current: float = None,
                      num_devices: int = None,
                      info: str = None,
                      db: psycopg2.extensions.connection = None,
                      cur: psycopg2.extensions.cursor = None):
        
        statement = f"""insert into group_tb ("group", "current", "num_devices", "info") values('{group}', {current}, {num_devices}, '{info}');"""
        try:
            cur.execute(statement)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
        return DB.execute(f"""select * from group_tb where "group" = '{group}'""", db)
