
from elasticsearch import Elasticsearch

from django.conf import settings 
es = Elasticsearch(**settings.ES_CONFIG)


def search_client(q, page):
	per_page = 5
	f = (page - 1) * per_page

	body = {
	"query": {
		"query_string": {
			"fields": ["name", "country_grouping", "location"],
			"query": q,
		}
		},

		"from": f,
		"size": per_page,
	}

	return es.search(index="foreign", doc_type='client', body=body)

def search_registrant(q, page):
	per_page = 5
	f = (page - 1) * per_page

	body = {
	"query": {
		"query_string": {
			"fields": ["name"],
			"query": q,
		}
		},

		"from": f,
		"size": per_page,
	}

	return es.search(index="foreign", doc_type='registrant', body=body)

def search_recipients(q, page):
	per_page = 10
	f = (page - 1) * per_page

	body = {
	"query": {
		"query_string": {
			"fields": ["name", "office", "agency"],
			"query": q,
		}
		},

		"from": f,
		"size": per_page,
	}

	return es.search(index="foreign", doc_type='people_org', body=body)

def search_arms(q, page):
	per_page = 10
	f = (page - 1) * per_page

	body = {
	"query": {
		"query_string": {
			"fields": ["title", "text", "location"],
			"query": q,
		}
		},

		"from": f,
		"size": per_page,
	}

	return es.search(index="foreign", doc_type='arms', body=body)

def search_interactions(q, page):
	per_page = 20
	f = (page - 1) * per_page

	body = {
	"query": {
		"query_string": {
			"fields": ["client", "registrant", "recipient", "purpose", "contributor", "subcontractor", ],
			"query": q,
		}
		},

		"from": f,
		"size": per_page,
	}

	return es.search(index="foreign", doc_type='interactions', body=body)

def search_locations(q, page):
	per_page = 20
	f = (page - 1) * per_page

	body = {
	"query": {
		"query_string": {
			"fields": ["location", "region"],
			"query": q,
		}
		},

		"from": f,
		"size": per_page,
	}

	return es.search(index="foreign", doc_type='location', body=body)

def search_text(q, page):
	per_page = 20
	f = (page - 1) * per_page

	body = {
	"query": {
		"query_string": {
			"fields": ["text"],
			"query": q,
		}
		},

		"from": f,
		"size": per_page,
	}

	return es.search(index="foreign", doc_type='fara_files', body=body)


## tests
# page = 1

# q = "China"
# clients = search_client(q, page)

# print len(clients), "clients"

# q = "Podesta"
# regs = search_registrant(q, page)

# print len(regs), "regs"

# q = "Pelosi"
# people_org = search_recipients(q, page)

# print len(people_org), "peeps"

# q = "Arabia"
# arms = search_arms(q, page)

# print len(arms), "arms"

# q = "Congress"
# interactions = search_interactions(q, page)

# print len(interactions), "inter"

