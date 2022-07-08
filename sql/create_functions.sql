------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------
/*
	  This script install functions in the database
*/
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------


/*
    This is the function requred to generate an empty component table every time an asset type 
    is created. 
*/
create or replace function generate_table()
  returns trigger as 
   $$ 
    begin
      execute format('create table "%s_%s_tb"(id int primary key not null references asset_tb(id));', new."type", new."subtype");
    return new;
  end;
  $$
  language 'plpgsql';

/*
    This generates the trigger for the above function.
*/
create trigger generate_table_trigger
	after insert 
	on asset_type_tb
	for each row 
	execute procedure generate_table();
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------










