import itertools
from logging import debug

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

from fara_feed.models import Document
from FaraData.models import MetaData, Registrant

processed_true = [] 
reviewed_true = []
names = {}
doctype = {}
notes = {}

def make_pages(form, page):
    paginator = Paginator(form, 10)
    try:
        form = paginator.page(page)
    except PageNotAnInteger:
        form = paginator.page(1)
    except EmptyPage:
        form = paginator.page(paginator.num_pages)
    
    for d in form: 
        try:
            docdata = MetaData.objects.get(link=d.url)
            reviewed = docdata.reviewed
            if reviewed == True:
                reviewed_true.append(str(docdata.link))
                
            processed = docdata.processed
            if processed == True:
                processed_true.append(str(docdata.link))

            notes[d.url] = docdata.notes
            
        except MetaData.DoesNotExist:
            continue
    
    for d in form:  
        try:
            debug(Registrant.objects.get(reg_id=int(d.reg_id)))
            reg = Registrant.objects.get(reg_id=d.reg_id)
            names[d.reg_id] = reg.reg_name
        except Registrant.DoesNotExist:
            continue
    
    return form 

def fast_pages(form, page):
    paginator = Paginator(form, 10)
    try:
        form = paginator.page(page)
    except PageNotAnInteger:
        form = paginator.page(1)
    except EmptyPage:
        form = paginator.page(paginator.num_pages)
    return form

@login_required(login_url='/admin')
def fast_supplemental(request):
    supplementals = Document.objects.filter(doc_type = "Supplemental", processed=False).order_by('-stamp_date')
    page = request.GET.get('page')
    supplementals = make_pages(supplementals, page)
    
    return render_to_response('fara_feed/supplemental_choices.html', { 'supplementals' : supplementals,
                                                            'processed_true': processed_true,
                                                            'reviewed_true': reviewed_true,
                                                            'notes': notes,
                                                            'names': names,
        })

@login_required(login_url='/admin')
def full_list(request):
    sf_page = request.GET.get('sf_page')
    ab_page = request.GET.get('ab_page')
    o_page = request.GET.get('o_page')
    a_page = request.GET.get('a_page')
    
    supplementals = Document.objects.filter(doc_type = 'Supplemental').order_by('-stamp_date')
    s_page = request.GET.get('s_page')
    supplementals = make_pages(supplementals, s_page)
    
    registrations = Document.objects.filter(doc_type = 'Registration').order_by('-stamp_date') 
    r_page = request.GET.get('r_page')
    registrations = make_pages(registrations, r_page)

    amendments = Document.objects.filter(doc_type = 'Amendment').order_by('-stamp_date')
    a_page = request.GET.get('a_page')
    amendments = make_pages(amendments, a_page)
    
    short_forms = Document.objects.filter(doc_type = 'Short Form').order_by('-stamp_date')
    short_forms = fast_pages(short_forms, sf_page)

    ab = Document.objects.filter(doc_type = 'Exhibit AB').order_by('-stamp_date')
    ab_page = request.GET.get('ab_page')
    ab = make_pages(ab, ab_page)
    
    others = Document.objects.filter(doc_type__in=['Exhibit C', 'Exhibit D', 'Conflict Provision']).order_by('-stamp_date')
    o_page = request.GET.get('o_page')
    others = fast_pages(others, o_page)
    
    return render_to_response('fara_feed/doc_choices.html', { 'supplementals' : supplementals,
                                                    'registrations': registrations,
                                                    'amendments' : amendments,
                                                    'short_forms' : short_forms,
                                                    'ab': ab,
                                                    'others': others,
                                                    'processed_true': processed_true,
                                                    'reviewed_true': reviewed_true,
                                                    'notes': notes,
                                                    'names': names,
    })


@login_required(login_url='/admin')
def entry_list(request):
    entry_docs = Document.objects.filter(doc_type__in=['Supplemental', 'Registration', 'Amendment', 'Exhibit AB' ], processed=False).order_by('stamp_date')
    page = request.GET.get('page')
    entry_docs = make_pages(entry_docs, page)
    
    return render_to_response('fara_feed/entry_list.html', {'entry_docs' : entry_docs,
                                                            'processed_true': processed_true,
                                                            'reviewed_true': reviewed_true,
                                                            'notes': notes,
                                                            'names': names,
     })