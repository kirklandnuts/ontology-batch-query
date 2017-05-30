# Batch Query Ontologies in Python
This is a module for batch querying ontologies using [BioPortal's API](http://data.bioontology.org/documentation) to resolve a list of terms.

## Usage
```
>>> from batch_query import *
```

### Resolving a single term
```
>>> melanoma_matches = resolve_term('melanoma')
```
The variable `melanoma_matches` contains a list of dictionaries, with each dictionary representing an individual resolution through an ontology on BioPoral.

To clarify, the variable `melanoma_matches` contains the list `collection` from within [the nested JSON object representing the response](http://data.bioontology.org/search?q=melanoma). NOTE: This function only captures non-naked terms (those with provided definitions). 

Accessing the definition from the first match in the list of matches:

```
>>> melanoma_matches[0]['definition']
['A malignant neoplasm derived from cells that are capable of forming melanin, which may occur in the skin of any part of the body, in the eye, or, rarely, in the mucous membranes of the genitalia, anus, oral cavity, or other sites. It occurs mostly in adults and may originate de novo or from a pigmented nevus or malignant lentigo. Melanomas frequently metastasize widely, and the regional lymph nodes, liver, lungs, and brain are likely to be involved. The incidence of malignant skin melanomas is rising rapidly in all parts of the world. (Stedman, 25th ed; from Rook et al., Textbook of Dermatology, 4th ed, p2445)']

```

### Resolving a list of terms
```
>>> terms = ['fish','bird','dog']
>>> resolved_terms = resolve_list(terms)
```
`resolve_list()` simply calls `resolve_term()` on each term in the list argument and returns them in a structured form. Here, `resolved_terms` contains a list of dictionaries, with each dictionary representing a searched term and all of its matches. Here it is visualized:

```
[
	{
		'term':'fish', 
		'matches':<RETURNED VALUE FROM resolve_terms('fish')>
	},
	{
		'term':'bird', 
		'matches':<RETURNED VALUE FROM resolve_terms('bird')>
	},
	{
		'term':'dog', 
		'matches':<RETURNED VALUE FROM resolve_terms('dog')>
	}
]
```

## To-do
- output results to .csv
- consider unresolvable terms