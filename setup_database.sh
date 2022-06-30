#!/bin/bash

################################################################################
################################################################################
#
#        This script will promt the user to 
#            1. install PostgreSQL
#            2. install timescale db
#            3. setup the database and user
#            4. setup the table schema 
#            5. enable timescaledb extension
#
#
#
#        Tim Darrah
#        NASA Fellow
#        PhD Student
#        Vanderbilt University
#        timothy.s.darrah@vanderbilt.edu
#
################################################################################
################################################################################


###  install PostgreSQL  ###
############################
read -p "install postgreSQL? (y/n): " ans
if [[ $ans = y ]]
then
    # Create the file repository configuration:
    sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

    # # Import the repository signing key:
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

    # # Update the package lists:
    sudo apt-get update

    # # Install the latest version of PostgreSQL.
    # # If you want a specific version, use 'postgresql-12' or similar instead of 'postgresql':
    sudo apt-get -y install postgresql postgresql-contrib
fi
unset ans


###  install timescale  ###
###########################
read -p "install timescaledb? (y/n): " ans
if [[ $ans = y ]]
then
    ./install_timescale.sh
fi
unset ans


###  create the database and user  ###
######################################
read -p "setup database? (y/n): " ans
if [[ $ans = y ]]
then
    read -p "enter your password: " PASSWORD
    read -p "enter the database name: " DB_NAME
    sudo -u postgres psql -f sql/setup_user_database.sql -v user="$USER" -v passwd="'$PASSWORD'" -v db_name="$DB_NAME"
fi
unset ans


###  create the tables  ###
###########################
read -p "setup table schema? (y/n): " ans
if [[ $ans = y ]]
then
    psql -d $DB_NAME -f sql/create_framework_tables.sql -U $USER 
    psql -d $DB_NAME -f sql/create_functions.sql -U $USER
fi
unset ans


###  enable timescale extension  ###
####################################
read -p "enable timescaledb extension? (y/n): " res
if [[ $res = y ]]
then
    psql -d $DB_NAME -f sql/enable_timescale.sql -U $USER 
fi
unset res


echo 'restarting postgresql service...'
sudo service postgresql restart
echo 'service restarted.'
echo 'configuration complete.'


