from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response

from fara_feed.models import Document
from FaraData.models import MetaData

def full_list(request):
    docs = Document.objects.all()
    supplementals = []
    short_forms = []
    ab = []
    others = []
    amendments = []
    processed_true = []
    reviewed_true = []
    
    for d in docs:
        if d.doc_type == "Supplemental":
            supplementals.append(d)
            try:
                docdata = MetaData.objects.get(link=d.url)
                processed_true.append(docdata.link)
                reviewed =  docdata.reviewed
                if reviewed == True:
                    reviewed_true.append(docdata.link)
            except:
                print "ok"
    	elif d.doc_type =="Amendment":
            amendments.append(d)
            try:
                docdata = MetaData.objects.get(link=d.url)
                processed_true.append(docdata.link)
                reviewed =  docdata.reviewed
                if reviewed == True:
                    reviewed_true.append(docdata.link)
            except:
                print "ok"
    	elif d.doc_type == "Short Form":
    		short_forms.append(d)
    	elif d.doc_type == "Exhibit AB":
    		ab.append(d)
    	else:
    		others.append(d)
        
    print reviewed_true
    supplementals = sorted(supplementals, key=lambda document: document.stamp_date, reverse=True)
    return render_to_response('doc_choices.html', { 'supplementals' : supplementals,
                                                    'amendments' : amendments,
                                                    'short_forms' : short_forms,
                                                    'ab': ab,
                                                    'others': others,
                                                    'processed_true': processed_true,
                                                    'reviewed_true': reviewed_true,
        })

