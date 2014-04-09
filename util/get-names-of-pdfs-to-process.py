#!/usr/bin/env python
# get-names-of-pdfs-to-process.py
#
# $1 -- type of pdf to process . technically these are the keys to_s3_path
#       right now just "fara" and "arms"
#
# currently relies on pdf2htmlEX but NOT the virtualenv for fara . all
# hardcoded paths are now at the top of this file ... so it doubles as it's own
# config file !
#
# --timball@sunlightfoundation.com Wed Nov 27 19:06:33 UTC 2013

DEBUG = False
PROCESS_INDEX = '/projects/fara/src/fara/util/process-index.sh'
global thing   # i needed a global

to_s3_path = {
                'fara':  {'html': 's3://fara.sunlightfoundation.com/html',
                          'pdf': 's3://fara.sunlightfoundation.com/pdfs',
                          'html_dest_dir': '/mnt/html',
                          'pdf_dest_dir': '/mnt/fara-pdfs'},
                'arms':  {'html': 's3://fara.sunlightfoundation.com/arms_html',
                          'pdf': 's3://fara.sunlightfoundation.com/arms_pdf',
                          'html_dest_dir': '/mnt/arms_html',
                          'pdf_dest_dir': '/mnt/arms_pdfs'},
             }

import subprocess 
import os
import sys

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
    get_pdf_cmd_raw = "s3cmd get %s/" % (to_s3_path[thing]['pdf'])
    pdf2htmlEX_cmd_raw = "pdf2htmlEX --embed cfijo --external-hint-tool=ttfautohint --dest-dir "

    for i in diff_list:
        get_pdf_cmd = get_pdf_cmd_raw + i + '.pdf'
        pdf2htmlEX_cmd = "%s %s/%s %s/%s.pdf index.html" % (pdf2htmlEX_cmd_raw, to_s3_path[thing]['html_dest_dir'], i, to_s3_path[thing]['pdf_dest_dir'], i)

        if not DEBUG:
            #print "get_pdf_cmd: " + get_pdf_cmd
            subprocess.call(get_pdf_cmd, shell=True) # this puts things in to pwd 
            os.rename(i+'.pdf', to_s3_path[thing]['pdf_dest_dir']+"/"+i+'.pdf') 
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
    process_index_cmd = "%s %s %s" % (PROCESS_INDEX, basename, to_s3_path[thing]['html_dest_dir'])
    
    if not DEBUG:
        #print process_index_cmd
        subprocess.call(process_index_cmd, shell=True)
    else:
        print process_index_cmd


def put_to_s3(basename):
    s3sync_cmd = "s3cmd put --recursive %s/%s %s/" % (to_s3_path[thing]['html_dest_dir'], basename, to_s3_path[thing]['html'])

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
    s3_setacl_cmd = "s3cmd setacl %s/%s --acl-public --recursive" % (to_s3_path[thing]['html'], basename)

    if not DEBUG:
        subprocess.call(s3_setacl_cmd, shell=True) 
        subprocess.call("s3cmd setacl s3://fara.sunlightfoundation.com/javascript/ --acl-public --recursive", shell=True)
        subprocess.call("s3cmd setacl s3://fara.sunlightfoundation.com/css/ --acl-public --recursive", shell=True)
        subprocess.call("s3cmd setacl s3://fara.sunlightfoundation.com/html/ --acl-public --recursive", shell=True)
    else:
        print "s3_set_acl_cmd: " + s3_setacl_cmd


def make_the_dirs():
    import os

    try:
        os.mkdir(to_s3_path[thing]['pdf_dest_dir'])
        os.mkdir(to_s3_path[thing]['html_dest_dir'])
    except OSError as e:
        sys.stderr.write("Error: %s: %s\n" % (e.errno, e.strerror))
        pass


def main(argv):
    pdfs = []
    htmls = []

    make_the_dirs()
    # this where i'm lazy and just call Popen FIXME right way is to use boto and query myself ... remember this is Popen so subprocess doesn't actually run until you look and will hard block until it's done
    get_htmls_raw = "s3cmd ls %s/ | awk '/DIR/ {print $2}'" % (to_s3_path[thing]['html'])
    if DEBUG:
        print get_htmls_raw
    get_htmls_cmd = subprocess.Popen(get_htmls_raw, shell=True, stdout=subprocess.PIPE)
    
    get_pdfs_raw = "s3cmd ls %s/ | awk '/pdf$/ {print $4}'" % (to_s3_path[thing]['pdf']) 
    if DEBUG:
        print get_pdfs_raw
        #sys.exit(1)
    get_pdfs_cmd = subprocess.Popen(get_pdfs_raw, shell=True, stdout=subprocess.PIPE)

    # get a list of files that s3 has for 
    htmls = make_list_from_stdout(get_htmls_cmd.stdout)
    pdfs = make_list_from_stdout(get_pdfs_cmd.stdout, ext='.pdf')

    # munge things 
    htmls = munge_html(htmls)
    pdfs = munge_pdfs(pdfs)

    diff = list(set(pdfs).difference(htmls))

    for i in diff:
        print i
    # now get each pdf and then process them into html files 
#    process_diff(diff)


if __name__ == "__main__":
    global thing
    if ((len(sys.argv) != 2) or (sys.argv[1] == 'fara') or (sys.argv[1] == 'arms')):
        thing = sys.argv[1]
        main(sys.argv[1:])
    else:
        sys.stderr.write("%s [fara|arms]\n" % (sys.argv[0]))
        sys.exit(1)

# vim: set shiftwidth=4 tabstop=4 expandtab:
