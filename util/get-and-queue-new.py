#!/usr/bin/env python
#
# --timball@sunlightfoundation.com
# Wed Nov 27 19:06:33 UTC 2013

DEBUG = False
HTML_DEST_DIR = '/mnt/html'
PDF_DEST_DIR = '/mnt/fara-pdfs'
PROCESS_INDEX = '/mnt/process-index.sh'

import subprocess 
import os

def make_list_from_stdout (stdout_thing, **kwargs):
    # $1 -- ideally an itterable that is the output from a Popen
    # $2 -- a dict w/ option ext='.foo' where .foo is the extension to strip from the response
    # return -- list that has been stripped of newlines and possibly extension
    ret_list = []

    for line in stdout_thing:
        item = line.rstrip()
        if (kwargs.has_key('ext')):
            item = item.replace(kwargs['ext'], '')
        ret_list.append(item)
    return(ret_list)


def process_diff(diff_list):
    # $1 -- list of pdfs to get and convert into html directories
    # os.chdir(workdir) # should do this ... but probably okay to not .
    get_pdf_cmd_raw = "s3cmd get s3://fara.sunlightfoundation.com/pdfs/"
    pdf2htmlEX_cmd_raw = "pdf2htmlEX --embed cfijo --external-hint-tool=ttfautohint --dest-dir "

    for i in diff_list:
        get_pdf_cmd = get_pdf_cmd_raw + i + '.pdf'
        pdf2htmlEX_cmd = "%s %s/%s %s/%s.pdf" % (pdf2htmlEX_cmd_raw, HTML_DEST_DIR, i, PDF_DEST_DIR, i)

        if not DEBUG:
            #print "get_pdf_cmd: " + get_pdf_cmd
            subprocess.call(get_pdf_cmd, shell=True) # this puts things in to pwd 
            os.rename(i+'.pdf', PDF_DEST_DIR+"/"+i+'.pdf') 
            #print "pdf2htmlEX_cmd: " + pdf2htmlEX_cmd
            subprocess.call(pdf2htmlEX_cmd, shell=True)
            #print "process_index(%s)" % (i)
            process_index(i)
            put_to_s3(i)
            s3_set_acls(i)
        else:
            print get_pdf_cmd
            print pdf2htmlEX_cmd
            process_index(i)
            put_to_s3(i)
            s3_set_acls(i)


def process_index(basename):
    #from cStringIO import StringIO
    #from contextlib import closing
    #with open(basename+".pdf") as fin: 
    #print "process_index: " + basename
    process_index_cmd = "%s %s %s" % (PROCESS_INDEX, basename, "/mnt/html")
    
    if not DEBUG:
        #print process_index_cmd
        subprocess.call(process_index_cmd, shell=True)
    else:
        print process_index_cmd


def put_to_s3(basename):
    s3sync_cmd = "s3cmd put --recursive %s/%s s3://fara.sunlightfoundation.com/html/" % (HTML_DEST_DIR, basename)

    if not DEBUG:
        subprocess.call(s3sync_cmd, shell=True)
    else: 
        print s3sync_cmd

def munge_html(s3_list):
    ret_list = []

    for i in s3_list:
        item = os.path.basename(os.path.dirname(i))
        ret_list.append(item)
    return ret_list


def munge_pdfs(s3_list):
    ret_list = []

    for i in s3_list:
        ret_list.append(os.path.splitext(os.path.basename(i))[0])
    return ret_list


def s3_set_acls(basename):
    s3_setacl_cmd = "s3cmd setacl s3://fara.sunlightfoundation.com/html/%s --acl-public --recursive" % (basename)

    if not DEBUG:
        subprocess.call(s3_setacl_cmd, shell=True) 
    else:
        print "s3_set_acl_cmd: " + s3_setacl_cmd


def main():
    pdfs = []
    htmls = []

    # this where i'm lazy and just call Popen FIXME right way is to use boto and query myself ... remember this is Popen so subprocess doesn't actually run until you look and will hard block until it's done
    get_htmls_cmd = subprocess.Popen("s3cmd ls s3://fara.sunlightfoundation.com/html/ | awk '/DIR/ {print $2}'", shell=True, stdout=subprocess.PIPE)
    
    get_pdfs_cmd = subprocess.Popen("s3cmd ls s3://fara.sunlightfoundation.com/pdfs/ | awk '/pdf$/ {print $4}'", shell=True, stdout=subprocess.PIPE)

    # get a list of files that s3 has for 
    htmls = make_list_from_stdout(get_htmls_cmd.stdout)
    pdfs = make_list_from_stdout(get_pdfs_cmd.stdout, ext='.pdf')

    # munge things 
    htmls = munge_html(htmls)
    pdfs = munge_pdfs(pdfs)

    diff = list(set(pdfs).difference(htmls))

    # now get each pdf and then process them into html files 
    process_diff(diff)


if __name__ == "__main__":
    main()
# vim: set shiftwidth=4 tabstop=4 expandtab:
