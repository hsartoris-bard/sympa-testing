#!/bin/bash
#
#read -s -p "SQL root password:" SQLROOT
#echo " "
#read -s -p "SQL sympa password:" SQLSYMPA
#echo " "
#
#DBDUMP="/home/smaguire/sympa02_db_dump_20181107.sql.gz"
#DBDUMPFILE="sympa02_db_dump_20181107.sql"
#
#echo "----Current settings----"
#echo "Loading database from: ${DBDUMP}"
#
#echo "WARNING: proceeding beyond this point will remove ALL Sympa entries from MySQL, list_data, and arc"
#while true; do
#	read -p "Continue? [yes/*] " yn
#	case $yn in
#		yes ) break;;
#		* ) exit;;
#	esac
#done
#
#echo "Stopping services"
#sudo systemctl stop sympa
#sudo systemctl stop wwsympa
#
#echo "Deleting old database and creating new one"
#mysql --user=root --password=$SQLROOT << EOF
#DROP DATABASE sympa;
#CREATE DATABASE sympa CHARACTER SET utf8;
#GRANT ALL PRIVILEGES ON sympa.* TO sympa@localhost IDENTIFIED BY "${SQLSYMPA}";
#QUIT
#EOF
#
#echo "Copying in database"
#TMPDIR=`mktemp -d`
#sudo cp $DBDUMP $TMPDIR
#gzip -d $TMPDIR/*
#echo `ls $TMPDIR`
#echo `file $TMPDIR/$DBDUMPFILE`
#mysql --user=root --password=$SQLROOT sympa < $TMPDIR/$DBDUMPFILE
#
echo "Removing old lists and archives"
# this is dumb
rm -r /var/lib/sympa/list_data/sympa.bard.edu/
mkdir /var/lib/sympa/list_data/sympa.bard.edu
rm -r /var/lib/sympa/arc/
mkdir /var/lib/sympa/arc


echo "Copying in new lists and archives"
echo "Take this opportunity to make sure the sympa database has the right password"
echo "syntax: GRANT ALL PRIVILEGES ON sympa.* TO sympa@localhost IDENTIFIED BY <password>"
echo "Except <password> needs to be in quotes"
# this will take care of removing old files, transferring data, and taking ownership
python36 migrate_data.py overwrite

# this is gonna need reauthentication, probably
#
#echo "Upgrading Sympa database"
#sudo -i sympa.pl --upgrade --from=6.1.19 --to=6.2.37b.2
#
#echo "Restarting services"
#sudo systemctl start sympa
#sudo systemctl start wwsympa
#
#echo "Migration complete"
#
#echo "rsync -rR --chown=sympa:sympa --exclude-from=blacklist <src> <dst> "
