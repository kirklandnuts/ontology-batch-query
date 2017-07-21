# Batch Query Ontologies in Python
This is a module for batch querying ontologies using [BioPortal's API](http://data.bioontology.org/documentation) to resolve a list of terms.

## Usage

### Command Line functionality
arguments:
```
./batch_query.py -h
usage: batch_query.py [-h] [-o OUTPUT_FILE] [-s SCOPE [SCOPE ...]] [-n LIMIT]
                      directory input_file

Resolve a list of terms by querying ontologies on BioPortal

positional arguments:
  directory
  input_file

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        manually set a name for the output file (default =
                        <input_file>_resolved.csv)
  -s SCOPE [SCOPE ...], --scope SCOPE [SCOPE ...]
                        designates a scope of ontologies for the program to
                        query
  -n LIMIT, --limit LIMIT
                        designates a numerical limit for number of matches to
                        be returned for each query
```
Querying term in measurements.txt, only returning matches from SWEET and RCD ontologies (by default, the program returns matches from all ontologies) and with a numerical limit of 23 matches returned per query (by default, this limit is 25 (good balance between variety of matches returned and speed of query)).
```
./batch_query.py ./examples/measurements/ measurements.txt -s SWEET RCD -n 23

Your scope is:  ['SWEET', 'RCD']

The script will return a maximum of 23 matches per query.

The terms in ./examples/measurements/measurements.txt have been resolved through BioPortal.

Results have been stored in ./examples/measurements/measurements_resolved_20170721T130755.csv.
```
Both `measurements.txt` and `measurements_resolved_20170721T130755.csv` can be found in the `./examples/` directory of this repo.

### Importing functions for use in other script or in python console
```
>>> from batch_query import *
```

#### Resolving a single term
```
>>> melanoma_matches = resolve_term('melanoma')
```

The variable `melanoma_matches` contains a list of dictionaries, with each dictionary representing an individual resolution through an ontology on BioPortal. To clarify, the variable `melanoma_matches` contains the list `collection` from within [the nested JSON object representing the response](http://data.bioontology.org/search?q=melanoma) with some additional information added to each element of the list (done in `additional_elements()`).

Accessing the definition from the first match in the list of matches:

```
>>> melanoma_matches[0]['definition']
['A malignant neoplasm derived from cells that are capable of forming melanin, which may occur in the skin of any part of the body, in the eye, or, rarely, in the mucous membranes of the genitalia, anus, oral cavity, or other sites. It occurs mostly in adults and may originate de novo or from a pigmented nevus or malignant lentigo. Melanomas frequently metastasize widely, and the regional lymph nodes, liver, lungs, and brain are likely to be involved. The incidence of malignant skin melanomas is rising rapidly in all parts of the world. (Stedman, 25th ed; from Rook et al., Textbook of Dermatology, 4th ed, p2445)']
```

#### Resolving a list of terms
```
>>> terms = ['fish','bird','dog']
>>> resolved_terms = resolve_list(terms)
```
`resolve_list()` simply calls `resolve_term()` on each term in the list argument and returns them in a structured form. Here, `resolved_terms` is a list of lists of dictionaries, with each nested list representing a searched term and with each dictionary within that list representing a single match. Here it is visualized:

```
[
	[
		{<FIRST ELEMENT OF LIST RETURNED FROM resolve_term('fish')>}
		{<SECOND ELEMENT OF LIST RETURNED FROM resolve_term('fish')>}
		...
		{<Nth ELEMENT OF LIST RETURNED FROM resolve_term('fish')>}
	],
	[
		{<FIRST ELEMENT OF LIST RETURNED FROM resolve_term('bird')>}
		{<SECOND ELEMENT OF LIST RETURNED FROM resolve_term('bird')>}
		...
		{<Nth ELEMENT OF LIST RETURNED FROM resolve_term('bird')>}
	],
	[
		{<FIRST ELEMENT OF LIST RETURNED FROM resolve_term('dog')>}
		{<SECOND ELEMENT OF LIST RETURNED FROM resolve_term('dog')>}
		...
		{<Nth ELEMENT OF LIST RETURNED FROM resolve_term('dog')>}
	]
]
```

where N = the limit of matches returned per query


## Notes
### Other Features
[BioPortal's API documentation](http://data.bioontology.org/documentation) shows its other capabilities. Because I am not 100% sure about our ultimate goal with this script, I don't know what other features I can implement involving its extra capabilities. Please let me know if there is anything else I can add to this script/module to make it more useful.
