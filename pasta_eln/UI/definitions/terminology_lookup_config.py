""" Configuration for terminology lookup services. """
from typing import Any
lookupConfig:list[dict[str, Any]] = []


# Wikipedia configuration
# requests.get('https://en.wikipedia.org/w/rest.php/v1/search/page',
#              params={'q': 'force', 'limit': 5},
#              headers={'User-Agent': 'PASTA-ELN (https://github.com/PASTA-ELN/pasta-eln)'},
#              timeout=10)
lookupConfig.append({
    "name": "wikipedia",
    "url": "https://en.wikipedia.org/w/rest.php/v1/search/page",
    "search_term_key": "q",
    "request_params": {
      "q": "searchTerm",
      "limit": 5
    },
    "header": {
      "User-Agent": "PASTA-ELN (https://github.com/PASTA-ELN/pasta-eln)"
    },
    "iri_prefix": "https://en.wikipedia.org/w/index.php?curid=",
    "search_criteria": {
      "results_keys": [
        "pages"
      ],
      "description_keys": [
        "description"
      ],
      "id_key": "id"
    },
    "skip_description": "Topics referred to by the same term",
    "icon_name": "wikipedia.png"
  })


# Wikidata configuration
# requests.get('https://www.wikidata.org/w/api.php',
#              params={'search': 'force', 'action': 'wbsearchentities', 'format': 'json', 'language': 'en', 'type': 'item', 'continue': '0'},
#              headers={'User-Agent': 'PASTA-ELN (https://github.com/PASTA-ELN/pasta-eln)'},
#              timeout=10)
lookupConfig.append({
    "name": "wikidata",
    "url": "https://www.wikidata.org/w/api.php",
    "search_term_key": "search",
    "request_params": {
      "search": "searchTerm",
      "action": "wbsearchentities",
      "format": "json",
      "language": "en",
      "type": "item",
      "continue": "0"
    },
    "header": {
      "User-Agent": "PASTA-ELN (https://github.com/PASTA-ELN/pasta-eln)"
    },
    "search_criteria": {
      "results_keys": [
        "search"
      ],
      "description_keys": [
        "display",
        "description",
        "value"
      ],
      "id_key": "concepturi"
    },
    "icon_name": "wikidata.png"
  })


# Ontology Lookup Service (OLS) configuration
# requests.get('http://www.ebi.ac.uk/ols/api/search',
#              params={'q': 'force'},
#              headers={},
#              timeout=10)
lookupConfig.append({
    "name": "ontology_lookup_service",
    "url": "http://www.ebi.ac.uk/ols/api/search",
    "search_term_key": "q",
    "request_params": {
      "q": "searchTerm"
    },
    "search_criteria": {
      "results_keys": [
        "response",
        "docs"
      ],
      "description_keys": [
        "description"
      ],
      "id_key": "iri"
    },
    "icon_name": "ols.png"
  })


# TIB Terminology Service configuration
# requests.get('https://service.tib.eu/ts4tib/api/search',
#              params={'q': 'force'},
#              headers={'Caller': 'PASTA_ELN'},
#              timeout=10)
lookupConfig.append({
    "name": "tib_terminology_service",
    "url": "https://service.tib.eu/ts4tib/api/search",
    "search_term_key": "q",
    "request_params": {
      "q": "searchTerm"
    },
    "header": {
      "Caller": "PASTA_ELN"
    },
    "duplicate_ontology_names": [
      "afo", "bco", "bto", "chiro", "chmo", "duo", "edam", "efo", "fix", "hp", "iao", "mod", "mop", "ms",
      "nmrcv", "ncit", "obi", "om", "pato", "po", "proco", "prov", "rex", "ro", "rxno", "sbo", "sepio", "sio",
      "swo", "t4fs", "uo"
    ],
    "search_criteria": {
      "results_keys": [
        "response",
        "docs"
      ],
      "description_keys": [
        "description"
      ],
      "id_key": "iri",
      "ontology_name_key": "ontology_name"
    },
    "icon_name": "tib.png"
  })
