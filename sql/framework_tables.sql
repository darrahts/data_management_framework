
create extension if not exists timescaledb;

create table process_type_tb(
	"id" serial primary key not null,
	"type" varchar(32) not null,
	"subtype1" varchar(64) not null,
	"subtype2" varchar(64),
	unique("type", "subtype1", "subtype2")
);

create table process_tb(
	"id" serial primary key not null,
	"type_id" int not null references process_type_tb,
	"description" varchar(256) not null,
    "source" varchar(256) not null,
	"parameters" json not null,
	unique("type_id", "description", "source")
);

create table asset_type_tb(
    "id" serial primary key not null,
    "type" varchar(32) not null,
    "subtype" varchar(32) not null,
    "description" varchar(256),
    unique ("type", "subtype")
);

create table group_tb(
	"id" serial primary key not null,
	"group" varchar(24) unique not null,
	"current" float,
	"num_devices" int,
	"info" varchar(256)
);
insert into group_tb("group", "info") values('none', 'placeholder');

create table asset_tb(
    "id" serial primary key not null,
    "type_id" int not null references asset_type_tb(id),
    "group_id" int not null references group_tb(id),
    "owner" varchar(32) not null default(current_user),
	"process_id" int references process_tb(id),
    "serial_number" varchar(32) unique not null default upper(substr(md5(random()::text), 0, 9)),
	"common_name" varchar(32),
    "age" float not null default 0,
    "eol" float,
    "rul" float,
    "units" varchar(32),
    unique("type_id", "owner", "process_id", "common_name", "age", "eol", "rul", "units")
);









