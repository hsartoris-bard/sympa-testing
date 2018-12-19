#!/bin/bash

rsync -az --itemize-changes --exclude-from=/home/hsartoris/blacklist_arc root@sympa02.bard.edu:/usr/local/sympa/arc/ /var/lib/sympa/arc/

rsync -az --itemize-changes --exclude-from=/home/hsartoris/blacklist_list_data root@sympa02.bard.edu:/usr/local/sympa/list_data/sympa.bard.edu/ /var/lib/sympa/list_data/sympa.bard.edu/
