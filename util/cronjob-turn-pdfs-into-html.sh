#!/bin/bash
#
# cronjob-turn-pdfs-into-html.sh
#
# $1 -- type of pdfs to process ... currently [arms|fara]
#
# intended use it to be call this script by cron
#

WORK_DIR=$(pwd)
cd $WORK_DIR

lockfile -r 0 $WORK_DIR/lockfile || exit 1

TYPE=$1
case $TYPE in
	fara)
		PDF_DIR="pdfs"
		HTML_DIR="html"
		;;
	arms)
		PDF_DIR="arms_pdf"
		HTML_DIR="arms_html"
		;;
	*)
		echo "bad juju"
		exit 1
		;;
esac

# python script gets a list of names to update 
# htmly-pdf.sh takes one pdf name. gets it and then calls pdf2htmlEX
# for fara 
./get-names-of-pdfs-to-process.py $TYPE 2> /dev/null | parallel --max-procs=8 ./htmly-pdf.sh {} $PDF_DIR $HTML_DIR

# random sleep
sleep 2

# put all the files up to s3 and make them public (-g public-read) and only put files that are new (-w)
#time boto-rsync -w -g public-read $HTML_DIR s3://fara.sunlightfoundation.com/$HTML_DIR/

rm -f $WORK_DIR/lockfile
