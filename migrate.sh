#!/bin/bash

read -s -p "SQL root password:" SQLROOT
echo " "
read -s -p "SQL sympa password:" SQLSYMPA
echo " "
SQLSTRING="CREATE DATABASE sympa CHARACTER SET utf8; GRANT ALL PRIVILEGES ON sympa.* to sympa@localhost IDENTIFIED BY ${SQLSYMPA};"

DBDUMP="/home/smaguire/sympa02_db_dump_20181107.sql.gz"

FROMDIR="/mnt/sympa02_files/"
TODIR="/var/lib/sympa/"

echo "----Current settings----"
echo "Loading database from: ${DBDUMP}"
echo "Copying lists and archives from: ${FROMDIR}"
echo "Copying lists and archives to: ${TODIR}"

echo "WARNING: proceeding beyond this point will remove ALL Sympa entries from MySQL, list_data, and arc"
while true; do
	read -p "Continue? [yes/*] " yn
	case $yn in
		yes ) break;;
		* ) exit;;
	esac
done

echo "Deleting old database"

echo mysql -u root -p$SQLROOT -e "DROP DATABASE sympa;"
exit 
sudo rm -r /var/lib/sympa/list_data/sympa.bard.edu/*
sudo rm -r /var/lib/sympa/arc/*

# this will take care of transferring data and ownership
sudo python3 migrate_data.py $FROMDIR $TODIR



