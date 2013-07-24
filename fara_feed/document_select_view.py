import itertools

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

from fara_feed.models import Document
from FaraData.models import MetaData

processed_true = [] 
reviewed_true = []
doctype = {}
notes = {}

def make_pages(form, page):
    paginator = Paginator(form, 20)
    try:
        form = paginator.page(page)
    except PageNotAnInteger:
        form = paginator.page(1)
    except EmptyPage:
        form = paginator.page(paginator.num_pages)
    
    for d in form:    
        try:
            docdata = MetaData.objects.get(link=d.url)
            processed_true.append(docdata.link)
            reviewed =  docdata.reviewed
            if reviewed == True:
                reviewed_true.append(docdata.link)
            notes[d.url] = docdata.notes
        except:
            continue
    return form 

@login_required(login_url='/admin')
def fast_supplemental(request):
    supplementals = Document.objects.filter(doc_type = "Supplemental")
    supplementals = sorted(supplementals, key=lambda document: document.id)
    page = request.GET.get('page')
    supplementals = make_pages(supplementals, page)
    
    return render_to_response('fara_feed/supplemental_choices.html', { 'supplementals' : supplementals,
                                                            'processed_true': processed_true,
                                                            'reviewed_true': reviewed_true,
                                                            'notes': notes,
        })

@login_required(login_url='/admin')
def full_list(request):
    processed_true = []
    reviewed_true = []

    sf_page = request.GET.get('sf_page')
    ab_page = request.GET.get('ab_page')
    o_page = request.GET.get('o_page')
    
    supplementals = Document.objects.filter(doc_type = 'Supplemental')
    supplementals = sorted(supplementals, key=lambda document: document.id)
    s_page = request.GET.get('s_page')
    supplementals = make_pages(supplementals, s_page)
    
    registrations = Document.objects.filter(doc_type = 'Registration')
    registrations = sorted(registrations, key=lambda document: document.id) 
    r_page = request.GET.get('r_page')
    registrations = make_pages(registrations, r_page)

    amendments = Document.objects.filter(doc_type = 'Amendment')
   
    # these don't even have the crappy stamp date in url maybe add date in processing?
    a_page = request.GET.get('a_page')
    amendments = make_pages(amendments, a_page)
    amendments = sorted(amendments, key=lambda document: document.id)
    
    short_forms = Document.objects.filter(doc_type = 'Short Form')
    short_forms = sorted(short_forms, key=lambda document: document.id)
    short_forms = make_pages(short_forms, sf_page)

    ab = Document.objects.filter(doc_type = 'Exhibit AB')
    ab = sorted(ab, key=lambda document: document.id)
    ab = make_pages(ab, ab_page)
    
    others = []
    other_forms = ['Exhibit C', 'Exhibit D', 'Conflict Provision']
    for other in other_forms:
        docs = Document.objects.filter(doc_type = other) 
        others.append(docs)
    
    others = list(itertools.chain(*others))
    # don't have stamp dates
    others = make_pages(others, o_page)
    
    return render_to_response('fara_feed/doc_choices.html', { 'supplementals' : supplementals,
                                                    'registrations': registrations,
                                                    'amendments' : amendments,
                                                    'short_forms' : short_forms,
                                                    'ab': ab,
                                                    'others': others,
                                                    'processed_true': processed_true,
                                                    'reviewed_true': reviewed_true,
                                                    'notes': notes,
    })


@login_required(login_url='/admin')
def entry_list(request):
    processed_true = []
    reviewed_true = []

    page = request.GET.get('page')

    entry_docs = []
    
    forms = ['Supplemental', 'Registration', 'Amendment', 'Exhibit AB', 'Conflict Provision']
    
    for kind in forms:
        docs = Document.objects.filter(doc_type=kind, processed=False) 
        entry_docs.append(docs)

    entry_docs = list(itertools.chain(*entry_docs))
    entry_docs  = sorted(entry_docs , key=lambda document: document.id) 
    entry_docs = make_pages(entry_docs, page)
    
    return render_to_response('fara_feed/entry_list.html', {'entry_docs' : entry_docs,
                                                            'processed_true': processed_true,
                                                            'reviewed_true': reviewed_true,
                                                            'notes': notes,
     })

