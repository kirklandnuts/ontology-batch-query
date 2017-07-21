#!/usr/bin/env python3


# -- HEADER --

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
import argparse
from warnings import warn


# -- GLOBAL VARIABLES --

REST_URL = 'http://data.bioontology.org'
API_KEY = 'a2580539-56ae-420f-b558-3ab624285dbe'
STORED_ONTOLOGIES = {}
MIN_KEYS = ['prefLabel', 'definition', 'synonym', '@id']
ALL_KEYS = ['searched_term','prefLabel', 'definition', 'synonym', 'ontology_acronym', 'ontology_name', 'last_updated', 'has_child', 'parents', '@id']


# -- FUNCTIONS --

# precondition: The first argument is a path to a text file that contains a list of terms to be searched separated
#   by newline characters. The second argument is a path to a directory in which the csv containing the batch
#   query results is to be outputted. The optional third argument is is a list of strings, each string being a
#   (CASE SENSITIVE) acronym associated with an ontology. This list of acronyms is the subset of ontologies from which
#   the function will return matches. By default, this function considers all ontologies.
# postcondition: Outputs a csv file containing matches from ontologies on Bioportal for the searched terms
def output_batch_query(directory, input_filename, output_filename, ontologies_param = None, n_matches = 25):
    input_path = os.path.join(directory, input_filename)
    output_path = os.path.join(directory, output_filename)
    if ontologies_param is None:
        ontologies_param = []
    # populating a list with terms from the input file
    terms_file = open(input_path, 'r')
    terms = []
    for line in terms_file:
        terms.append(line.strip())
    # use resolve_list() to resolve list of terms
    results_list = resolve_list(terms, ontologies_param, n_matches) # list of lists each representing the matches of a term and
    #   containing dictionaries of which each represent a single match
    # creating output csv file
    f = csv.writer(open(output_path, 'w'))
    f.writerow(["searched_term", "matched_term", "definition", "synonyms", "ontology_acronym", "ontology_name",
               "last_updated", "has_child", "parent(s)" ,"URL"])
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
def resolve_list(list_of_terms, ontologies_param = None, n_matches = 25):
    if ontologies_param is None:
        ontologies_param = []
    search_results = []
    for term in list_of_terms:
        search_results.append(resolve_term(term, ontologies_param, n_matches))
    return search_results


# precondition: The first argument is a string representation of the searched term. The second argument is a list of
#   strings, each string being a (CASE SENSITIVE) acronym associated with an ontology. This list of acronyms is the
#   subset of ontologies from which the function will return matches.
# postcondition: Returns a list of dicts, each dict representing a match from the query
def resolve_term(term, ontologies_param = None, n_matches = 25): # 25 numerical limit is arbitrary
    if ontologies_param is None:
        ontologies_param = []
    # generate query and use it to get the initial page of matches
    page = get_json(REST_URL + term_query_string(term, ontologies_param))
    matches_provided = page['totalCount']
    if matches_provided == 0: # handling unresolvable terms
        warn('WARNING: \'%s\' could not be resolved on BioPortal.' % term)
        return []
    else:
        # iterate through all pages, appending each one to a list of pages
        pages = list()
        if matches_provided < n_matches:  # ensuring that we don't exceed the number of matches provided by bioportal
            n_matches = matches_provided
        if n_matches >= 50:
            n_pages = n_matches // 50  # number of full pages to iterate through
            n_matches_last_page = n_matches % 50  # number of matches to retrieve from the last page
            pages.append(page['collection'])  # first page
            while len(pages) < n_pages:
                page = get_json(page['links']['nextPage'])
                pages.append(page['collection'])
            if n_matches_last_page != 0:  # grabbing excess matches
                page = get_json(page['links']['nextPage'])
                pages.append(page['collection'][:n_matches_last_page])
        else:
            pages.append(page['collection'][:n_matches])
        # extract matches from each page in list of pages and inserts them into a list of matches, adding some additional
        #   information to each match ('ontology_acronym', 'ontology_name', 'last_updated', and 'has_child')
        complete_matches = []
        for page in pages:
            for match in page:
                complete_match = additional_elements(match, term)
                time.sleep(.15)  # waiting to prevent timing out
                complete_matches.append(complete_match) # inserting the newly completed match into the list of matches
        return complete_matches


def additional_elements(match, term):
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
    match['has_child'] = get_json(match['links']['children'])['totalCount'] > 0
    # adding key 'parent(s)' with string representation of any parent terms or 'NA' if none exist
    match['parents'] = get_parents(match)
    return match


# takes a dictionary representing a single match from a query as an argument
# returns string containing parent classes or 'NA' if none exist
def get_parents(match):
    parents = get_json(match['links']['parents'])
    output = 'NA'
    if len(parents) > 0:
        output = []
        for parent in parents:
            output.append(parent['prefLabel'])
    return output


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

    parser = argparse.ArgumentParser(description='Resolve a list of terms by querying ontologies on BioPortal')

    parser.add_argument('directory')
    parser.add_argument('input_file')
    parser.add_argument('-o', '--output_file', default=None,
                        help = 'manually set a name for the output file (default = <input_file>_resolved.csv)')
    parser.add_argument('-s', '--scope', nargs='+', default=None,
                        help = 'designates a scope of ontologies for the program to query')
    parser.add_argument('-n', '--limit', default=25,
                        help='designates a numerical limit for number of matches to be returned for each query')

    args = parser.parse_args()

    directory = args.directory
    input_file = args.input_file
    time_stamp = time.strftime('%Y%m%dT%H%M%S')

    if args.output_file:
        output_file = args.output_file
    else:
        output_file = input_file[:-4] + '_resolved_' + time_stamp + '.csv'
    scope = args.scope
    limit = int(args.limit)

    if scope == None:
        print('\nYou have not defined a scope; the program will query all ontologies.')
    else:
        print('\nYour scope is: ', scope)
    output_batch_query(directory, input_file, output_file, scope, limit)
    print("\nThe terms in %s/%s have been resolved through BioPortal.\n\nResults have been stored in %s/%s.\n"
          % (directory, input_file, directory, output_file))



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

