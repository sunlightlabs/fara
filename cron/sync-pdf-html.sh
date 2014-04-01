#!/bin/bash
#
# sync-pdf-html.sh
#
# helper cron script .
# makes a log file so it doesn't double run .
#
# --timball@sunlightfoundation.com 
# Wed Feb 19 19:43:47 UTC 2014

WRK_DIR="/mnt"
SCRIPT="/projects/fara/src/fara/util/get-and-queue-new.py"

# test for lockfile
if [ -f $WRK_DIR/lock ]
then
    echo "already running!"
    exit 0
else
    echo "$(date) | PID: $$" >> $WRK_DIR/lock
fi

# do work 
cd $WRK_DIR
/projects/fara/virt/bin/python $SCRIPT fara
/projects/fara/virt/bin/python $SCRIPT arms

# done . cleanup lockfile
rm -f $WRK_DIR/lock
                                                                     1,1           All
