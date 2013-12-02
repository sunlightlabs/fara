#!/usr/bin/env python
#
# --timball@sunlightfoundation.com
# Wed Nov 27 19:06:33 UTC 2013

DEBUG = True
HTML_DEST_DIR = '/mnt/html'
PDF_DEST_DIR = '/mnt/fara-pdfs'

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
            subprocess.call(get_pdf_cmd)
            subprocess.call(pdf2htmlEX_cmd)
            os.rename(i+'.pdf', PDF_DEST_DIR) # this puts things in to pwd
            process_index(i)
        else:
            print get_pdf_cmd
            print pdf2htmlEX_cmd


def process_index(basename):
    #from cStringIO import StringIO
    #from contextlib import closing
    #with open(basename+".pdf") as fin: 
    print "process_index: " + basename


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

#    print "=========HTML============"
#    for i in htmls:
#        print i
#    print "=========PDFS============"
#    for i in pdfs: 
#        print i
#    # figure out what's in pdfs that isn't in htmls
    diff = list(set(pdfs).difference(htmls))

    # now get each pdf and then process them into html files 
    process_diff(diff)


if __name__ == "__main__":
    main()
# vim: set shiftwidth=4 tabstop=4 expandtab:
