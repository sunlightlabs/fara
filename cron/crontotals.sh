#! /bin/bash


source $HOME/virt/bin/activate

cd /projects/fara/src/fara
/projects/fara/virt/bin/python manage.py create_form_downloads > $HOME/cron/create_downloads.log 2>&1
/projects/fara/virt/bin/python manage.py totaler > $HOME/cron/totaler.log 2>&1

