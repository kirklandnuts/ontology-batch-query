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
def output_batch_query(inputPath, outputPath):
    # populating a list with terms from the input file
    terms_file = open(inputPath, 'r')
    terms = []
    for line in terms_file:
        terms.append(line)

    # use resolve_list() to resolve list of terms
    results_list = resolve_list(terms)

    # creating output csv file
    outfile = outputPath + '/resolved_terms.csv'
    f = csv.writer(open(outfile, 'wb'))
    f.writerow(["searched term", "matched term", "definition", "synonyms", "URL"])
    # populating csv with matches
    for dict in results_list:
        for match in dict['matches']:
            try:
                f.writerow(dict['term'], match['prefLabel'], match['definition'], match['synonym'], match['@id'])
            except KeyError:
                f.writerow(dict['term'], match['prefLabel'], match['definition'], NA, match['@id'])


# precondition: Argument is a list full of strings of terms to be resolved
# postcondition: Returns a list of dictionaries each representing a searched term and its matches
def resolve_list(listOfTerms):
    search_results = []
    for term in listOfTerms:
        result_dict = {'term':term, 'matches':resolve_term(term)}
        search_results.append(result_dict)

# precondition: Argument is a string representation of the searched term
# postcondition: Returns a list of JSON objects, each object representing an ontology entry that matches with the
#   searched term
def resolve_term(term):
    all_matches = get_json(REST_URL + '/search?q=' + term)['collection']
    #only interested in non-naked terms (those which have definitions)
    kept_matches = []
    for match in all_matches:
        if 'definition' in match.keys():
            kept_matches.append(match)
    return(kept_matches)

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
