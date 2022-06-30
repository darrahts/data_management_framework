------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------
/*
	This is the table schema for the core tables in the data management framework. It includes the following tables 
	
	- process_type_tb
	- process_tb   
	- asset_type_tb
	- asset_tb
	- group_tb
	- data_tb (called summary_tb in previous publications)


	Tim Darrah
	NASA Fellow
	PhD Student
	Vanderbilt University
	timothy.s.darrah@vanderbilt.edu
	
	For a more complete description and example implementation, see the README.md
*/
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------


-- timescale improves database performance
create extension if not exists timescaledb;


/*	process_type_tb

	brief: 
		holds meta data about a given process.

	fields:
		type: refers to the process such as degradation, environment, etc
		subtype1: refers to the component such as battery, motor, wind, etc
		subtype2: refers to what within the component such as capacitance, resistance, gust, etc
*/
create table process_type_tb(
	"id" serial primary key not null,
	"type" varchar(32) not null,
	"subtype1" varchar(64) not null,
	"subtype2" varchar(64),
	unique("type", "subtype1", "subtype2")
);
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------


/*	process_tb

	brief:
		Contains information and parameters for a model to either be implemented in simulation
		or fit to data. 
		
	fields:
		description: details about how the process evolves such as continuous or discrete, etc
		source: where the model was taken from such as a publication or experimentation, etc
		parameters: the process parameters as a json string
*/
create table process_tb(
	"id" serial primary key not null,
	"type_id" int not null references process_type_tb,
	"description" varchar(256) not null,
    	"source" varchar(256) not null,
	"parameters" json not null,
	unique("type_id", "description", "source")
);
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------


/*	group_tb

	brief: 
		table to group components by various means (such as a given run to failure experiment)

	fields:
		group: the name of the group
		info: information about the group
*/
create table group_tb(
	"id" serial primary key not null,
	"group" varchar(24) unique not null,
	"info" varchar(256)
);
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------


/*	asset_type_tb

	brief: 
		holds meta data about a given asset

	fields:
		type: refers to the asset type such as battery, transistor, etc
		subtype: refers to further specification of the asset
		description: any info about the asset desired
*/
create table asset_type_tb(
	"id" serial primary key not null,
	"type" varchar(32) not null,
	"subtype" varchar(32) not null,
	"description" varchar(256),
	unique ("type", "subtype")
);
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------


/*	asset_tb

	brief: 
		Core table of the framework that links all tables together. 

	fields:
		type_id: the id of the type of asset
		group_id: the id of group
		process_id: the id of the process (if one)
		owner: the user who created / owns the asset
		serial_number: unique serial number 
		common_name: simple name referencing the asset
		age, eol, rul: to track the life of the asset
		units: units of age, eol, and rul
*/
create table asset_tb(
	"id" serial primary key not null,
	"type_id" int not null references asset_type_tb(id),
	"group_id" int not null references group_tb(id),
	"process_id" int references process_tb(id),
	"owner" varchar(32) not null default(current_user),
	"serial_number" varchar(32) unique not null default upper(substr(md5(random()::text), 0, 9)),
	"common_name" varchar(32),
	"age" float not null default 0,
	"eol" float,
	"rul" float,
	"units" varchar(32),
	unique("type_id", "owner", "process_id", "common_name", "age", "eol", "rul", "units")
);
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------


/*	asset_tb

	brief: 
		Core table of the framework that links all tables together. 

	fields:
		asset_id: the id of the asset that generated this data
		group_id: the id of group
		dt: timestamp of the generated data
		cycle: the cycle number of the generated data 
*/
create table data_tb(
    "id" serial not null,
    "asset_id" int not null references asset_tb(id),
    "group_id" int not null references group_tb(id),
    "dt" timestamp(3) not null,
    "cycle" int,
    primary key("group_id", "asset_id", "dt")
);
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------










