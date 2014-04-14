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

FILE_BASENAME=$1
PDFS_DIR=$2
HTML_DIR=$3
PDF_FILE="$FILE_BASENAME.pdf"


if [ ! -d $2 ]
then
	echo "arg 2:$2 isn't a dir"
	exit 1
fi
echo "s3cmd ls s3://fara.sunlightfoundation.com/$PDFS_DIR/$FILE_BASENAME.pdf"

# get one pdf
boto-rsync s3://fara.sunlightfoundation.com/$PDFS_DIR/$FILE_BASENAME.pdf $PDFS_DIR

# use above function to call pdf2htmlEX
pdf2htmlEX --embed cfijo --external-hint-tool=ttfautohint --dest-dir $HTML_DIR/$FILE_BASENAME $PDFS_DIR/$PDF_FILE index.html

#thing pdfs/$1.pdf $3
