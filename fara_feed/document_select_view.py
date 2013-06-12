from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response

from fara_feed.models import Document

def full_list(request):
    docs = Document.objects.all()
    supplementals = []
    short_forms = []
    ab = []
    others = []
    amendments = []
    baseurl = "http://127.0.0.1:8000/"
    for d in docs:
    	if d.doc_type == "Supplemental":
    		supplementals.append(d)
    	elif d.doc_type =="Amendment":
    		amendments.append(d)
    	elif d.doc_type == "Short Form":
    		short_forms.append(d)
    	elif d.doc_type == "Exhibit AB":
    		ab.append(d)
    	else:
    		others.append(d)

    form_groups = [{"supplementals" : supplementals}, {'amendments' : amendments}, {'short_forms' : short_forms}, {'ab': ab}, {'others' : others}, baseurl]
    print form_groups
    return render_to_response('doc_choices.html', {'form_groups': form_groups})

