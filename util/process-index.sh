#!/bin/bash
# this is me being lazy and using sed instead of processing the crap in python
#
# --timball@sunlightfoundation.com
# Mon Dec  2 22:41:19 UTC 2013
# 
# $1 -- basename of file to work on typically $(basename $PDFNAME .pdf)
# $2 -- optional directory to write too 

html_dir="/mnt/html"

if [ $1 ]
then
	BASE_NAME=$1
elif [ -z $1 ]
then
	echo "YOU MUST GIVE ME A THING TO WORK ON!"
	exit 1
fi

HTML_DIR=${2:-$html_dir}

DEST_DIR=$HTML_DIR/$BASE_NAME

#echo "\$1 == $1"
#echo "\$DEST_DIR == $DEST_DIR"

#echo "mv $DEST_DIR/$1.html $DEST_DIR/index.html"
mv $DEST_DIR/$1.html $DEST_DIR/index.html

cat $DEST_DIR/index.html | sed 's/base.min.css/\/css\/base.min.css/' > $DEST_DIR/tmp1	
cat $DEST_DIR/tmp1 	 | sed 's/fancy.min.css/\/css\/fancy.min.css/' > $DEST_DIR/tmp2
#echo "cat $DEST_DIR/index.html | sed 's/base.min.css/\/css\/base.min.css/' > $DEST_DIR/tmp1"
#echo "cat $DEST_DIR/tmp1 	 | sed 's/fancy.min.css/\/css\/fancy.min.css/' > $DEST_DIR/tmp2"

## deal w/ js assets
cat $DEST_DIR/tmp2 | sed 's/compatibility.min.js/\/javascript\/compatibility.min.js/' > $DEST_DIR/tmp3
cat $DEST_DIR/tmp3 | sed 's/pdf2htmlEX.min.js/\/javascript\/pdf2htmlEX.min.js/' > $DEST_DIR/tmp4
#echo "cat $DEST_DIR/tmp2 | sed 's/compatibility.min.js/\/javascript\/compatibility.min.js/' > $DEST_DIR/tmp3"
#echo "cat $DEST_DIR/tmp3 | sed 's/pdf2htmlEX.min.js/\/javascript\/pdf2htmlEX.min.js/' > $DEST_DIR/tmp4"

mv $DEST_DIR/tmp4 $DEST_DIR/index.html
#echo "mv $DEST_DIR/tmp4 $DEST_DIR/index.html"

rm -f $DEST_DIR/tmp[1234] $DEST_DIR/base.min.css $DEST_DIR/fancy.min.css $DEST_DIR/compatibility.min.js $DEST_DIR/pdf2htmlEX.min.js
#echo "rm -f $DEST_DIR/tmp[1234] $DEST_DIR/base.min.css $DEST_DIR/fancy.min.css $DEST_DIR/compatibility.min.js $DEST_DIR/pdf2htmlEX.min.js"
