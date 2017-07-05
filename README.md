# Batch Query Ontologies in Python
This is a module for batch querying ontologies using [BioPortal's API](http://data.bioontology.org/documentation) to resolve a list of terms.

## Usage

### Command Line functionality
```
$ python3 batch_query.py /Users/timothy/Documents/ontology-batch-query/examples/measurements/measurements.txt


The terms in /Users/timothy/Documents/ontology-batch-query/examples/taxon/taxon.txt have been resolved through BioPortal.
Results have been stored in /Users/timothy/Documents/ontology-batch-query/examples/taxon/resolved_terms.csv.
```
Both of these files are included (along with others) in the `examples` folder in this repository.


### Importing functions for use in other script or in python console
```
>>> from batch_query import *
```

#### Resolving a single term
```
>>> melanoma_matches = resolve_term('melanoma')
```

The variable `melanoma_matches` contains a list of dictionaries, with each dictionary representing an individual resolution through an ontology on BioPortal. The BioPortal API limits each page response to containing no more than 50 matches. Resolve_term() handles the collection of the comprehensive set of matches with three lines of code (lines 79-81 in `batch_query.py`) that employ a while loop to iterate through all the available pages. Currently, I have commented out those three lines, limiting the amount of matches per searched term.

```
>>> len(melanoma_matches)
50
```

To clarify, the variable `melanoma_matches` contains the list `collection` from within [the nested JSON object representing the response](http://data.bioontology.org/search?q=melanoma) with some additional information added to each element of the list (done in `resolve_term()`).

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
		{<Kth ELEMENT OF LIST RETURNED FROM resolve_term('fish')>}
	],
	[
		{<FIRST ELEMENT OF LIST RETURNED FROM resolve_term('bird')>}
		{<SECOND ELEMENT OF LIST RETURNED FROM resolve_term('bird')>}
		...
		{<Mth ELEMENT OF LIST RETURNED FROM resolve_term('bird')>}
	],
	[
		{<FIRST ELEMENT OF LIST RETURNED FROM resolve_term('dog')>}
		{<SECOND ELEMENT OF LIST RETURNED FROM resolve_term('dog')>}
		...
		{<Nth ELEMENT OF LIST RETURNED FROM resolve_term('dog')>}
	]
]
```

where K, M, and N = the number of total matches returned by calling resolve_term() on 'fish', 'bird', and 'dog' respectively


## Notes
### Speed
Time to resolve the 4 terms in `measurements.txt` (found in `examples` folder) when amount of matches is limited to 50:
```
$ time python3 batch_query.py /Users/timothy/Documents/ontology-batch-query/examples/measurements/measurements.txt


The terms in /Users/timothy/Documents/ontology-batch-query/examples/measurements/measurements.txt have been resolved through BioPortal.
Results have been stored in /Users/timothy/Documents/ontology-batch-query/examples/measurements/resolved_terms.csv.


real	0m54.349s
user	0m1.205s
sys	0m0.202s
```

Here I do the same thing, this time without limiting the amount of matches per term, and had to interrupt the process before it could finish. I'm not sure how far it got, but it ran for a very long time before I stopped it:
```
$ time python3 batch_query.py /Users/timothy/Documents/ontology-batch-query/examples/measurements/measurements.txt
^CTraceback (most recent call last):
  File "batch_query.py", line 165, in <module>
    output_batch_query(inputFile, outputDirectory)
  File "batch_query.py", line 40, in output_batch_query
    results_list = resolve_list(terms, ontologies_param) # list of lists each representing the matches of a term and
  File "batch_query.py", line 63, in resolve_list
    search_results.append(resolve_term(term, ontologies_param))
  File "batch_query.py", line 102, in resolve_term
    time.sleep(.1)
KeyboardInterrupt

real	37m16.905s
user	0m12.848s
sys	0m1.973s
```


### Other Features
[BioPortal's API documentation](http://data.bioontology.org/documentation) shows its other capabilities. Because I am not 100% sure about our ultimate goal with this script, I don't know what other features I can implement involving its extra capabilities. Please let me know if there is anything else I can add to this script/module to make it more useful.

## To-do
- extend ontology scope functionality to command line use
- allow user inputted limit of matches per searched term
- improve output file naming procedure
	- currently outputs with the same filename every time (sorry)
- consider unresolvable terms
	- haven't run into one yet (haven't tried a wide variety of terms yet)
- clean code
	- standard naming convention
	- handle key custom encoding within resolve_term()
