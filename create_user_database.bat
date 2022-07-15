
set /p DB_NAME=Enter the name for your database:

echo username: %USERNAME%

set /p PASSWORD=Enter your password: 

psql -U postgres -c "create user %USERNAME% with encrypted password '%PASSWORD%'; alter user %USERNAME% with superuser;" 
psql -U postgres -c "create database uav_db with owner %USERNAME%;"

