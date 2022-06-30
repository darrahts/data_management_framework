------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------
/*
        This script will create a database and superuser with the currently logged in user.
*/
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------

-- create a database user (you)
create user :user with encrypted password :passwd;

-- give yourself admin access
alter user :user with superuser;

-- create the database
create database :db_name with owner :user;
