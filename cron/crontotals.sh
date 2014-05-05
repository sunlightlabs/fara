#! /bin/bash

source $HOME/virt/bin/activate

cd /projects/fara/src/fara
/projects/fara/virt/bin/python manage.py create_form_downloads --contacts > $HOME/cron/create_downloads.log 2>&1
/projects/fara/virt/bin/python manage.py create_form_downloads --payments > $HOME/cron/create_downloads.log 2>&1
/projects/fara/virt/bin/python manage.py create_form_downloads --disbursements > $HOME/cron/create_downloads.log 2>&1
/projects/fara/virt/bin/python manage.py create_form_downloads --contributions > $HOME/cron/create_downloads.log 2>&1
/projects/fara/virt/bin/python manage.py create_form_downloads --client_reg > $HOME/cron/create_downloads.log 2>&1
/projects/fara/virt/bin/python manage.py totaler > $HOME/cron/totaler.log 2>&1