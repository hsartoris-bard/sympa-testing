#!/bin/bash

read -s -p "SQL root password:" SQLPASS
exit

DBDUMP="/home/smaguire/sympa02_db_dump_20181107.sql.gz"

FROMDIR="/mnt/sympa02_files/"
TODIR="/var/lib/sympa/"

sudo rm -r /var/lib/sympa/list_data/sympa.bard.edu/*
sudo rm -r /var/lib/sympa/arc/*

# this will take care of transferring data and ownership
sudo python3 migrate_data.py $FROMDIR $TODIR


