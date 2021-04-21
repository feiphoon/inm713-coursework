"""
Created on 19 Jan 2021

@author: ejimenez-ruiz
"""
from owlready2 import *
from onto_access import OntologyAccess


def load_classes(uri_onto):
    onto_access = OntologyAccess(uri_onto)
    onto_access.loadOntology(True)

    results = onto_access.getClasses()

    for r in results:
        print(r)

def load_object_properties(uri_onto):
    onto_access = OntologyAccess(uri_onto)
    onto_access.loadOntology(True)

    results = onto_access.getObjectProperties()

    for r in results:
        print(r)


def load_data_properties(uri_onto):
    onto_access = OntologyAccess(uri_onto)
    onto_access.loadOntology(True)

    results = onto_access.getDataProperties()

    for r in results:
        print(r)


def load_individuals(uri_onto):
    onto_access = OntologyAccess(uri_onto)
    onto_access.loadOntology(True)

    results = onto_access.getIndividuals()

    for r in results:
        print(r)



# Load ontology
# urionto = "http://protege.stanford.edu/ontologies/pizza/pizza.owl"
# urionto = "http://www.cs.ox.ac.uk/isg/ontologies/schema.org.owl"
urionto = "http://www.cs.ox.ac.uk/isg/ontologies/dbpedia.owl"
load_classes(urionto)
# load_object_properties(urionto)
# load_data_properties(urionto)
# load_individuals(urionto)
