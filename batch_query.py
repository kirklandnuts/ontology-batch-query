## -- HEADER --

'''
Last updated on 6/13/17
Created on 5/18/17
Adapted by Timothy Nguyen, NCEAS from Bioportal API sample code:
    https://github.com/ncbo/ncbo_rest_sample_code/blob/master/python/classes_search.py
'''

import requests
import json
import csv
import os
import sys
import time
from warnings import warn


# -- GLOBAL VARIABLES --

REST_URL = 'http://data.bioontology.org'
API_KEY = 'a2580539-56ae-420f-b558-3ab624285dbe'
STORED_ONTOLOGIES = {}
MIN_KEYS = ['prefLabel', 'definition', 'synonym', '@id']
ALL_KEYS = ['searched_term','prefLabel', 'definition', 'synonym', 'ontology_acronym', 'ontology_name', 'last_updated', 'has_child', '@id']

# -- FUNCTIONS --

# precondition: The first argument is a path to a text file that contains a list of terms to be searched separated
#   by newline characters. The second argument is a path to a directory in which the csv containing the batch
#   query results is to be outputted. The optional third argument is is a list of strings, each string being a
#   (CASE SENSITIVE) acronym associated with an ontology. This list of acronyms is the subset of ontologies from which
#   the function will return matches. By default, this function considers all ontologies.
# postcondition: Outputs a csv file containing matches from ontologies on Bioportal for the searched terms
def output_batch_query(inputPath, outputPath, ontologies_param = None):
    if ontologies_param is None:
        ontologies_param = []
    # populating a list with terms from the input file
    terms_file = open(inputPath, 'r')
    terms = []
    for line in terms_file:
        terms.append(line.strip())
    # use resolve_list() to resolve list of terms
    results_list = resolve_list(terms, ontologies_param) # list of lists each representing the matches of a term and
    #   containing dictionaries of which each represent a single match
    # creating output csv file
    f = csv.writer(open(outputPath, 'w'))
    f.writerow(["searched_term", "matched_term", "definition", "synonyms", "ontology_acronym", "ontology_name",
               "last_updated", "has_child","URL"])
    # populating csv with matches
    for term_matches in results_list: # iterating through list of lists; each iteration is list of all matches for a term
        for match in term_matches: # iterating through list of dictionaries each representing a match
            record = []
            for key in ALL_KEYS:
                record.append(match[key])
            f.writerow(record)



# precondition: 1st argument is a list containing strings of terms to be resolved; The second argument is a list of
#   strings, each string being a (CASE SENSITIVE) acronym associated with an ontology. This list of acronyms is the
#   subset of ontologies from which the function will return matches.
# postcondition: Returns a list of lists of dictionaries with each nested list representing a searched term and
#   each dictionary within representing a match of the term
def resolve_list(listOfTerms, ontologies_param = None):
    if ontologies_param is None:
        ontologies_param = []
    search_results = []
    for term in listOfTerms:
        search_results.append(resolve_term(term, ontologies_param))
    return search_results


# precondition: The first argument is a string representation of the searched term. The second argument is a list of
#   strings, each string being a (CASE SENSITIVE) acronym associated with an ontology. This list of acronyms is the
#   subset of ontologies from which the function will return matches.
# postcondition: Returns a list of dicts, each dict representing a match from the query
def resolve_term(term, ontologies_param = None):
    if ontologies_param is None:
        ontologies_param = []
    # generate query and use it to get the initial page of matches
    page = get_json(REST_URL + term_query_string(term, ontologies_param))
    if page['totalCount'] == 0:
        warn('WARNING: \'%s\' could not be resolved on BioPortal.' % term)
        return []
    else:
        # iterate through all pages, appending each one to a list of pages
        pages = []
        pages.append(page)
        # COMMENT OUT THE NEXT 3 LINES TO LIMIT THE AMOUNT OF MATCHES TO 50 (max amount presented on the each page)
        # while (page['nextPage'] != None):
        #     page = get_json(page['links']['nextPage'])
        #     pages.append(page)
        # extract matches from each page in list of pages and inserts them into a list of matches, adding some additional
        #   information to each match ('ontology_acronym', 'ontology_name', 'last_updated', and 'has_child')
        matches = []
        for page in pages:
            for match in page['collection']:
                # handling missing values by checking against hard-coded list of minimum keys (global var: MIN_KEYS)
                for key in MIN_KEYS:
                    if key not in list(match.keys()):
                        match[key] = 'NA'
                # adding additional information before inserting the match into a list of matches
                # adding searched term
                match['searched_term'] = term
                # adding ontology info
                ontology_acronym = match['links']['ontology'][39:]
                if ontology_acronym not in STORED_ONTOLOGIES.keys():
                    STORED_ONTOLOGIES[ontology_acronym] = ontology_info(ontology_acronym)
                ontology = STORED_ONTOLOGIES[ontology_acronym]
                match['ontology_acronym'] = ontology_acronym
                match['ontology_name'] = ontology['name']
                match['last_updated'] = ontology['date']
                # adding key 'has_child' with boolean value representing whether or not the matched class has at least 1 child
                time.sleep(.2) # to avoid overloading BioPortal's API; .1s is as low as I've set the delay so there is room for experimentation
                match['has_child'] = get_json(match['links']['children'])['totalCount'] > 0

                # inserting the newly completed match into the list of matches
                matches.append(match)
        return matches
    # # THE FOLLOWING IS OBSOLETE B/C: (1) we want to capture naked terms, and (2) this condition can be passed as a
    # #     parameter in the query string
    # # we only interested in non-naked terms (those which have definitions)
    # kept_matches = []
    # for match in all_matches:
    #     if 'definition' in match.keys():
    #         kept_matches.append(match)
    # return(kept_matches)


# precondition: the argument is a string representation of an acronym used to identify an ontology
# postcondition: the function will return a list in which the first element is the string representation of the name of
#   the ontology from which the match was found and the second element is the date of the most recent update to the ontology
def ontology_info(acronym):
    ontology_query_string = REST_URL + '/ontologies/' + acronym + '/submissions'
    ontology = get_json(ontology_query_string)[0]
    my_ontology = {'name': ontology['ontology']['name'],
                   'date': ontology['creationDate'][:10]}
    return my_ontology


# precondition: The first argument is a string representation of the searched term. The second argument is a list of
#   strings, each string being a (CASE SENSITIVE) acronym associated with an ontology. This list of acronyms is the
#   subset of ontologies to be included in the query.
# postcondition: Constructs and returns a query string to be sent to BioPortal's API
def term_query_string(term, ontologies_param = None):
    if ontologies_param is None:
        ontologies_param = []
    search_term = 'q=' + term
    ontologies_phrase = 'ontologies=' + ','.join(ontologies_param)
    my_query = '/search?' + search_term + '&' + ontologies_phrase
    return(my_query)


# precondition: Argument is a string representation of the URL request to be made
# postcondition: Returns a dictionary representation of the json response object
def get_json(url):
    my_headers = {'Authorization':'apikey token='+API_KEY}
    r = requests.get(url, headers=my_headers)
    return(json.loads(r.text))



# -- MAIN --

# precondition: The first CLA should be a path to a text file that contains a list of terms to be searched separated
#   by newline characters. The optional second CLA should be a path to a directory in which the csv containing the batch
#   query results is to be outputted; if none is specified, the script will designate the directory containing the input
#   file as the output directory.
# postcondition: Calls output_batch_query() on the command line arguments
if __name__ == '__main__':
    if (len(sys.argv) > 1) or (len(sys.argv) < 2):
        try:
            inputFile = sys.argv[1]
            outputFile = sys.argv[2]
        except IndexError:
            inputFile = sys.argv[1]
            outputFile = os.path.dirname(inputFile) + 'resolved.csv'
        output_batch_query(inputFile, outputFile)
        print("\n\nThe terms in %s have been resolved through BioPortal.\nResults have been stored in %s/resolved_terms.csv.\n"
              % (inputFile, outputFile))
    else:
        print("\n\nUSAGE: python batch-query.py <input textfile> <*OPTIONAL* output directory>\n")


# # -- TESTING --
# children = []
# i = 1
# for link in links:
#     print(i)
#     time.sleep(.1)
#     children.append(get_json(link['children']))
#     i+=1
# for child in children:
#     print(child)
#
# eye = resolve_term('eye', [])
# print(eye[0].keys())
#
# for match in eye:
#     print(list(match.keys()))
#
# ALL_KEYS = ['searched_term','prefLabel', 'definition', 'synonym', 'ontology_acronym', 'ontology_name', 'last_updated', 'has_child', '@id']
# eye_records = []
# for match in eye:
#     record = []
#     for key in ALL_KEYS:
#         record.append(match[key])
#     eye_records.append(record)
#
# textfile_path = '/Users/timothy/Documents/ontology-batch-query/search-terms.txt'
# directory = '/Users/timothy/Documents/ontology-batch-query/'
# output_batch_query(inputPath = textfile_path,
#                    outputPath = directory,
#                    ontologies_param = None)
#
# debugging above call:
# terms_file = open(textfile_path, 'r')
# terms = []
# for line in terms_file:
#     terms.append(line.strip())
# # use resolve_list() to resolve list of terms
# results_list = resolve_list(terms, ontologies_param=[]) # list of lists each representing the matches of a term and
# #   containing dictionaries of which each represent a single match
# # creating output csv file
# outfile = directory + '/resolved_terms.csv'
# f = csv.writer(open(outfile, 'w'))
# f.writerow(["searched_term", "matched_term", "definition", "synonyms", "ontology_acronym", "ontology_name",
#            "last_updated", "has_child","URL"])
# # populating csv with matches
# for term_matches in results_list: # iterating through list of lists; each iteration is list of all matches for a term
#     for match in term_matches: # iterating throguh list of dictionaries each representing a match
#         record = []
#         for key in ALL_KEYS:
#             record.append(match[key])
#         f.writerow(record)

