#!/bin/bash


echo STOP! have you copied the database?
echo "mysqldump -u sympa -p --databases sympa > sympa02.sql"
echo check the sympa02 conf for pass
exit

echo Rsyncing

systemctl stop sympa wwsympa 

/home/hsartoris/sympa-testing/sync_to_sympa02.sh

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
