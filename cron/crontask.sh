#! /bin/bash


source $HOME/virt/bin/activate

cd /projects/fara/src/fara
/projects/fara/virt/bin/python manage.py create_feed > $HOME/cron/create_feed.log 2>&1
/projects/fara/virt/bin/python manage.py arms_sales_archive > $HOME/cron/arms_sales_archive.log 2>&1