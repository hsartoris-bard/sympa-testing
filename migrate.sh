#!/bin/bash

read -s -p "SQL root password:" SQLROOT
echo " "
read -s -p "SQL sympa password:" SQLSYMPA
echo " "
SQLSTRING="CREATE DATABASE sympa CHARACTER SET utf8; GRANT ALL PRIVILEGES ON sympa.* to sympa@localhost IDENTIFIED BY ${SQLSYMPA};"
echo $SQLSTRING
exit

DBDUMP="/home/smaguire/sympa02_db_dump_20181107.sql.gz"

FROMDIR="/mnt/sympa02_files/"
TODIR="/var/lib/sympa/"

sudo rm -r /var/lib/sympa/list_data/sympa.bard.edu/*
sudo rm -r /var/lib/sympa/arc/*

# this will take care of transferring data and ownership
sudo python3 migrate_data.py $FROMDIR $TODIR



