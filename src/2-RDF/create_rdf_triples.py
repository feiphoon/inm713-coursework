"""
Based heavily on code for lab6 of INM713.
Created on 05 March 2021
@author: ejimenez-ruiz
"""
import rdflib
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, XSD

import pandas as pd

from typing import Dict

from pprint import pprint


class TabToGraph:
    def __init__(self, input_filepath: str, namespace_str: str, prefix: str) -> None:
        self.input_filepath = input_filepath
        self.namespace_str = namespace_str
        self.prefix = prefix

        # Initialise graph
        self.graph = Graph()

        # Special Namespace class to directly create URIRefs
        self.namespace = Namespace(self.namespace_str)

        # Bind namespace
        self.graph.bind(self.prefix, self.namespace)

        # Load input as dataframe
        # TODO: consider using usecols here
        # TODO: datatypes along with that
        self.data_df = pd.read_csv(input_filepath)

        # Dictionary to store URIs
        self.string_to_uri = {}

    def convert_csv_to_rdf(self) -> None:
        if "currency" in self.data_df:

            # We give subject column and target type
            self.mapping_to_create_type_triple(
                subject_col="currency", class_type=self.namespace.Currency
            )

            self.mapping_to_create_literal_triple(
                subject_col="currency",
                object_col="currency",
                predicate=self.namespace.name,
                datatype=XSD.string,
            )

        if "currency" in self.data_df:

            # We give subject column and target type
            self.mapping_to_create_type_triple(
                subject_col="currency", class_type=self.namespace.Currency
            )

            self.mapping_to_create_literal_triple(
                subject_col="currency",
                object_col="currency",
                predicate=self.namespace.name,
                datatype=XSD.string,
            )

    @staticmethod
    def is_nan(x) -> bool:
        """Check for NaN when the subject value
        could be a string (so can't use math.isnan())
        """
        return x != x

    def createURIForEntity(self, entity_name: str) -> Dict[str, str]:
        # We create fresh URI (default option)
        self.string_to_uri[entity_name] = self.namespace_str + entity_name.replace(
            " ", "_"
        )

        # if useExternalURI:  # We connect to online KG
        #     uri = self.getExternalKGURI(name)
        #     if uri != "":
        #         self.stringToURI[name] = uri

        return self.string_to_uri[entity_name]

    def mapping_to_create_type_triple(
        self, subject_col: str, class_type: rdflib.term.URIRef
    ) -> None:
        """
        Mapping to create triples like lab6:London rdf:type lab6:City
        A mapping may create more than one triple
        column: columns where the entity information is stored
        useExternalURI: if URI is fresh or from external KG
        """
        for subject in self.data_df[subject_col]:
            entity_uri = None
            subject = subject.lower()

            # We use the ascii name to create the fresh URI for a city in the dataset
            if subject in self.string_to_uri:
                entity_uri = self.string_to_uri[subject]
            else:
                entity_uri = self.createURIForEntity(subject)
            # else:
            #     entity_uri = self.createURIForEntity(subject.lower(), useExternalURI)

            # TYPE TRIPLE
            # For the individuals we use URIRef to create an object "URI" out of the string URIs
            # For the concepts we use the ones in the ontology and we are using the NameSpace class
            # Alternatively one could use URIRef(self.lab6_ns_str+"City") for example
            self.graph.add((URIRef(entity_uri), RDF.type, class_type))

    def mapping_to_create_literal_triple(
        self, subject_col: str, object_col: str, predicate: str, datatype: str
    ) -> None:
        """
        Mappings to create triples of the form lab6:london lab6:name "London"
        """

        for subject, lit_value in zip(
            self.data_df[subject_col], self.data_df[object_col]
        ):

            # Make sure this does nothing when the object is missing
            if self.is_nan(lit_value) or lit_value is None or lit_value == "":
                return

            else:
                subject = subject.lower()
                # Use already created URI
                entity_uri = self.string_to_uri[subject]

                # Literal
                literal = Literal(lit_value, datatype=datatype)

                # Add new literal triple to graph
                self.graph.add((URIRef(entity_uri), predicate, literal))

    def debug(self):
        pprint(vars(self))


if __name__ == "__main__":
    # INPUT_FILEPATH = "../data/INM713_coursework_data_pizza_8358_1_reduced.csv"
    INPUT_FILEPATH = "../data/data_pizza_spike.csv"
    NAMESPACE = Namespace("http://www.city.ac.uk/ds/inm713/feiphoon#")
    PREFIX = "fp"

    tab_to_graph = TabToGraph(
        input_filepath=INPUT_FILEPATH, namespace_str=NAMESPACE, prefix=PREFIX
    )

    tab_to_graph.convert_csv_to_rdf()
    for s, p, o in tab_to_graph.graph:
        print((s.n3(), p.n3(), o.n3()))
