## -- HEADER --

'''
5/18/17
Adapted by Timothy Nguyen, NCEAS from Bioportal API sample code:
    https://github.com/ncbo/ncbo_rest_sample_code/blob/master/python/classes_search.py
'''

import requests
import json
import csv
import os
import sys

REST_URL = 'http://data.bioontology.org'
API_KEY = 'a2580539-56ae-420f-b558-3ab624285dbe'


## -- FUNCTIONS --

# precondition: The first argument is a path to a text file that contains a list of terms to be searched separated
#   by newline characters. The second argument is a path to a directory in which the csv containing the batch
#   query results is to be outputted
# postcondition: Outputs a csv file containing matches from ontologies on Bioportal for the searched terms
def output_batch_query(inputPath, outputPath, ontologies):
    # populating a list with terms from the input file
    terms_file = open(inputPath, 'r')
    terms = []
    for line in terms_file:
        terms.append(line.strip())
    # use resolve_list() to resolve list of terms
    results_list = resolve_list(terms, ontologies)
    # creating output csv file
    outfile = outputPath + '/resolved_terms.csv'
    f = csv.writer(open(outfile, 'w'))
    f.writerow(["searched_term", "matched_term", "definition", "synonyms", "URL"])
    # populating csv with matches
    # THIS WAS WRITTEN ASSUMING THAT ALL MATCHES HAD DEFINITIONS SO ITS BROKEN NOW BECAUSE MARK WANTS NAKED TERMS AS WELL
    #   GOOD JOB MARK YOU BROKE MY FUNCTION >:-(
    # for dict in results_list:
    #     for match in dict['matches']:
    #         try:
    #             f.writerow(dict['term'], match['prefLabel'], match['definition'], match['synonym'], match['@id'])
    #         except KeyError:
    #             f.writerow(dict['term'], match['prefLabel'], match['definition'], '', match['@id'])

# precondition: the argument is a dictionary representing a single match of a term from an ontology
# postcondition: the function will return True if the input match has at least one child term and False otherwise
def hasChild(match):
    children = get_json(match['links']['children'])
    return(children['totalCount'] > 0)

# precondition: the argument is a dictionary representing a single match of a term from an ontology
# postcondition: the function will return a list in which the first element is the string representation of the acronym
#   associated with the ontology from which the match was found and the second element is the date of the most recent
#   update to the ontology
def ontology_info(match):
    ontology = get_json(match['links']['ontology'])
    ontology_subs = get_json(ontology['links']['submissions'])
    my_ontology = {'name' : ontology['acronym'],
                   'date' : ontology_subs[0]['creationDate'][:10]}
    return(my_ontology)

# precondition: Argument is a list full of strings of terms to be resolved
# postcondition: Returns a list of dictionaries each representing a searched term and its matches
def resolve_list(listOfTerms, ontologies=None):
    if ontologies is None:
        ontologies = []
    search_results = []
    for term in listOfTerms:
        result_dict = {'term':term, 'matches':resolve_term(term, ontologies)}
        search_results.append(result_dict)
    return search_results

# precondition: The first argument is a string representation of the searched term. The second argument is a list of
#   strings, each string being a (CASE SENSITIVE) acronym associated with an ontology. This list of acronyms is the
#   subset of ontologies from which the function will return matches. By default, the function will consider all
#   ontologies.
# postcondition: Returns a list of dicts, each object representing a match from the query
def resolve_term(term, ontologies=None):
    if ontologies is None:
        ontologies = []
    # generate query and use it to get the initial page of matches
    query = query_string(term, ontologies)
    page = get_json(REST_URL + query)
    # iterate through all pages, appending each one to a list of pages
    pages = []
    pages.append(page)
    while (page['nextPage'] != None):
        page = get_json(page['links']['nextPage'])
        pages.append(page)
    # extract matches from each page in list of pages and insert them into a list of matches
    matches = []
    for page in pages:
        for match in page['collection']:
            matches.append(match)
    # grab other attributes 'ontology', 'lastUpdated', 'hasChildren', and 'hasParent'
    return(matches)
    # # THE FOLLOWING IS OBSOLETE B/C: (1) we want to capture naked terms, and (2) this condition can be passed as a
    # #     parameter in the query string
    # # we only interested in non-naked terms (those which have definitions)
    # kept_matches = []
    # for match in all_matches:
    #     if 'definition' in match.keys():
    #         kept_matches.append(match)
    # return(kept_matches)

# precondition: The first argument is a string representation of the searched term. The second argument is a list of
#   strings, each string being a (CASE SENSITIVE) acronym associated with an ontology. This list of acronyms is the
#   subset of ontologies to be included in the query.
# postcondition: Constructs and returns a query string to be sent to BioPortal's API
def query_string(term, ontologies=None):
    if ontologies is None:
        ontologies = []
    search_term = 'q=' + term
    ontologies_param = 'ontologies=' + ','.join(ontologies)
    my_query = '/search?' + search_term + '&' + ontologies_param
    return(my_query)

# precondition: Argument is a string representation of the URL request to be made
# postcondition: Returns a dictionary representation of the json response object
def get_json(url):
    myHeaders = {'Authorization':'apikey token='+API_KEY}
    r = requests.get(url, headers=myHeaders)
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
            outputDirectory = sys.argv[2]
        except IndexError:
            inputFile = sys.argv[1]
            outputDirectory = os.path.dirname(inputFile)
        output_batch_query(inputFile, outputDirectory)
        print("\nThe terms in %s have been resolved through BioPortal; Results have been stored in %s/resolved_terms.csv.\n"
              % (inputFile, outputDirectory))
    else:
        print("\nUSAGE: python batch-query.py <input textfile> <output directory>\n")
