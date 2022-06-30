/*
          Application specific fields for the iREL4.0 project
*/
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------


/*
   The group table contains additional info regarding the
   input current and the number of devices per round. In 
   addition, a group placeholder for the cooling block.
*/
alter table group_tb 
add column "current" float,
add column "num_devices" int;
insert into group_tb("group", "info") values('none', 'placeholder');
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------


/*
    the data table contains info regarding the cycle status,
    temperature, and voltage of the device
*/
alter table data_tb
add column "status" smallint,
add column "temperature" float,
add column "voltage" float;
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------


/*
    a secondary data table for cooling block data. All data tables have the same primary fields
    as the core data table. Then, additional columns are added.
*/
create table cb_data_tb as 
table data_tb 
with no data;

alter table cb_data_tb 
add column "block_temperature1" float,
add column "block_temperature2" float,
add column "water_temperature1" float,
add column "water_temperature2" float;
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------

/*
    enable timescale for cb_data_tb if timescale exists
*/
DO $$
BEGIN 
    IF EXISTS (select * from pg_available_extensions where name ilike 'timescaledb') THEN
        select create_hypertable('cb_data_tb', 'dt', chunk_time_interval => interval '14 days');
        select add_dimension('cb_data_tb', 'group_id', number_partitions => 4);
    END IF;
END $$;




