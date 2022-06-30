/*
          Application specific fields for the iREL4.0 project
*/



/*
   The group table contains additional info regarding the
   input current and the number of devices per round. In 
   addition, a group placeholder for the cooling block.
*/
alter table group_tb 
add column "current" float,
add column "num_devices" int;
insert into group_tb("group", "info") values('none', 'placeholder');



/*
    the data table contains info regarding the cycle status,
    temperature, and voltage of the device
*/
alter table data_tb
add column "status" smallint,
add column "temperature" float,
add column "voltage" float;


CREATE TABLE new_table AS 
TABLE existing_table 
WITH NO DATA;
