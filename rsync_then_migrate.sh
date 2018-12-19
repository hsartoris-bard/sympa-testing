#!/bin/bash

echo Rsyncing

systemctl stop sympa wwsympa 

/home/hsartoris/sympa-testing/sync_to_sympa02.sh

echo Still needs to import db, check bounce storage
exit

sympa.pl --upgrade --from=6.1.19 --to=6.2.37b.2

systemctl start sympa wwsympa postfix 

echo Adding aliases

for list in `ls /var/lib/sympa/list_data/sympa.bard.edu/`;
do
	echo $list
	alias_manager.pl add $list sympa.bard.edu
done

echo Reloading postfix

postfix reload

echo Done
