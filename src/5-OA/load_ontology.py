"""
Modified from INM713 lab code.

Created on 19 Jan 2021

@author: ejimenez-ruiz
"""
from owlready2 import *
from onto_access import OntologyAccess

from typing import Any
from pprint import pprint


def load_classes(uri_onto: str, print: bool = False) -> Any:
    """
    Returns objects of type owlready2.entity.ThingClass
    """
    onto_access = OntologyAccess(uri_onto)
    onto_access.loadOntology(True)
    results = onto_access.getClasses()

    if print:
        for _ in results:
            pprint(_)

    return [_ for _ in results]


def load_object_properties(uri_onto: str, print: bool = False):
    onto_access = OntologyAccess(uri_onto)
    onto_access.loadOntology(True)

    results = onto_access.getObjectProperties()

    if print:
        for _ in results:
            pprint(_)

    return [_ for _ in results]


def load_data_properties(uri_onto: str, print: bool = False):
    onto_access = OntologyAccess(uri_onto)
    onto_access.loadOntology(True)

    results = onto_access.getDataProperties()

    if print:
        for _ in results:
            pprint(_)

    return [_ for _ in results]


def load_individuals(uri_onto: str, print: bool = False):
    onto_access = OntologyAccess(uri_onto)
    onto_access.loadOntology(True)

    results = onto_access.getIndividuals()

    if print:
        for _ in results:
            pprint(_)

    return [_ for _ in results]


# Load ontology
# urionto = "http://protege.stanford.edu/ontologies/pizza/pizza.owl"
# urionto = "http://www.cs.ox.ac.uk/isg/ontologies/schema.org.owl"
# urionto = "http://www.cs.ox.ac.uk/isg/ontologies/dbpedia.owl"
# load_classes(urionto)
# load_object_properties(urionto)
# load_data_properties(urionto)
# load_individuals(urionto)
