/*
          Enable timescale extension to significantly improve database performance
          
          Must do this BEFORE data is added to the data table
          
          number of partitions or interval depends on the specific application.
          
          see https://docs.timescale.com/api/latest/hypertable/create_hypertable/#create-hypertable 
*/


create extension if not exists timescaledb;

select create_hypertable('data_tb', 'dt', chunk_time_interval => interval '14 days');
select add_dimension('data_tb', 'asset_id', number_partitions => 12);
select add_dimension('data_tb', 'group_id', number_partitions => 4);
create unique index idx_groupid_time on data_tb(group_id, asset_id, dt);

