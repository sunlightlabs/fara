#!/bin/bash
# 
# htmly-pdf.sh
#
# This script gets pdfs and then creates pdfs out of them 
#
# $1 -- name of pdf to deal w/ (no .pdf extension please)
# $2 -- directory to put pdfs into
# $3 -- directory to put html output too
#
# ./get-names-of-pdfs-to-process.py fara 2> /dev/null | parallel --max-procs=8 ./htmly-pdf.sh {} pdfs html

function do_one {
# $1 should be the name of the pdf
	HTML_DIR=$2
	FILE_NAME=$1
	PDFS_DIR=$(dirname $1)
	PDF=$(basename $1)
	FILE_BASENAME=$(basename $PDF .pdf)

#echo pdf2htmlEX --embed cfijo --external-hint-tool=ttfautohint --dest-dir $HTML_DIR/$FILE_BASENAME $PDFS_DIR/$PDF index.html
	pdf2htmlEX --embed cfijo --external-hint-tool=ttfautohint --dest-dir $HTML_DIR/$FILE_BASENAME $PDFS_DIR/$PDF index.html

#echo $FILE_BASENAME
}

if [ ! -d $2 ]
then
	echo "arg 2:$2 isn't a dir"
	exit 1
fi
echo "s3://fara.sunlightfoundation.com/pdfs/$1.pdf"

# get one pdf
boto-rsync s3://fara.sunlightfoundation.com/$2/$1.pdf $2

# use above function to call pdf2htmlEX
do_one pdfs/$1.pdf $3
