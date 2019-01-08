#!/bin/bash

if [ -z "$1" ] ; then
	echo STOP! have you copied the database?
	echo "mysqldump -u sympa -p --databases sympa > sympa02.sql"
	echo check the sympa02 conf for pass
	echo ALSO remember to do the whole GRANT ALL PRIVS etc to put in new password
	exit 1
fi

echo stopping sympa if running
systemctl stop sympa wwsympa 

echo "provided database dump: "
echo $1

read -p "SQL root password:" SQLROOT
read -p "SQL sympa password:" SQLSYMPA

# just in case
echo deleting old database
systemctl start mysql
mysql -u root --password=$SQLROOT << EOF
DROP DATABASE sympa;
CREATE DATABASE sympa CHARACTER SET utf8;
GRANT ALL PRIVILEGES ON sympa.* TO sympa@localhost IDENTIFIED BY "${SQLSYMPA}";
QUIT
EOF

echo importing database dump
mysql -u root --password=$SQLROOT sympa < $1

while true; do
	read -p "Everything look good to proceed to rsync? [y/N] " yn
	case $yn in
		y ) break;;
		Y ) break;;
		* ) exit;;
	esac
done

echo Rsyncing

/home/hsartoris/sympa-testing/sync_to_sympa02.sh

echo Upgrading
#sympa.pl --upgrade --from=6.1.19 --to=6.2.37b.2
sympa.pl --upgrade --from=6.1.19 --to=6.2.38


echo Adding aliases

for list in `ls /var/lib/sympa/list_data/sympa.bard.edu/`;
do
echo $list
alias_manager.pl add $list sympa.bard.edu
done

echo Reloading postfix
systemctl start sympa wwsympa postfix 
postfix reload

echo Done
