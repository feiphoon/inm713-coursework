"""
Based heavily on code for lab6 of INM713.
Created on 05 March 2021
@author: ejimenez-ruiz
"""
from pandas.core.frame import DataFrame
import rdflib
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, XSD, RDFS

import time
import pandas as pd
from unidecode import unidecode

from typing import Dict, Optional, Any

from pprint import pprint


class TabToGraph:
    def __init__(self, input_filepath: str, namespace_str: str, prefix: str) -> None:
        self.input_filepath: str = input_filepath
        self.namespace_str: str = namespace_str
        self.prefix: str = prefix

        # Initialise graph
        self.graph: rdflib.Graph = Graph()

        # Special Namespace class to directly create URIRefs
        self.namespace: rdflib.Namespace = Namespace(self.namespace_str)

        # Bind namespace
        self.graph.bind(self.prefix, self.namespace)

        # Load input as dataframe
        # TODO: consider using usecols here
        # TODO: datatypes along with that
        self.data_df: pd.DataFrame = pd.read_csv(input_filepath, encoding="utf-8")

        # Dictionary to store URIs
        self.string_to_uri: dict = {}

    @staticmethod
    def apply_preprocessing(
        df: pd.DataFrame, target_col: str, transformed_col: Optional[str]
    ) -> None:
        """
        A bit crude and does a lot of stuff, but it will do for now.
        Note, have tested all the bad characters in this dataset and
        how tolerant the URI creation is = there are some dangerous
        things like # and /, but it breaks on pipe character |.
        """
        # If no new col is named to hold transformations,
        # then the transformations should be in-place.
        if not transformed_col:
            print(
                "WARNING: transformed_col name not supplied, transformations will be applied in-place."
            )
            transformed_col = target_col

        # Normalise unicode/accented characters,
        # e.g. café becomes cafe.
        # TODO: buggy
        df[transformed_col] = df[target_col].apply(unidecode)

        # Check unique characters in menu item column
        unique_chars: list = list(set(df[transformed_col].sum()))

        non_alphanum_chars: list = [
            _ for _ in unique_chars if (not _.isalnum()) and (_ != " ")
        ]

        # Target some known troublemakers
        if "@" in non_alphanum_chars:
            df[transformed_col] = df[transformed_col].str.replace(
                "@", "at", regex=False
            )
            non_alphanum_chars.remove("@")

        if "&" in non_alphanum_chars:
            df[transformed_col] = df[transformed_col].str.replace(
                "&", "and", regex=False
            )
            non_alphanum_chars.remove("&")

        if "+" in non_alphanum_chars:
            df[transformed_col] = df[transformed_col].str.replace(
                "+", "and", regex=False
            )
            non_alphanum_chars.remove("+")

        # Remove sketchy characters
        for _ in non_alphanum_chars:
            df[transformed_col] = df[transformed_col].str.replace(_, "", regex=False)

        # Collapse remaining double whitespace,
        # possibly resulting from character removals.
        # E.g "Bonnie & Clyde" -> "Bonnie  Clyde"
        df[transformed_col] = df[transformed_col].str.replace(r" +", " ", regex=True)

    @staticmethod
    def replace_missing_values(
        df: DataFrame,
        target_col: str,
        transformed_col: Optional[str],
        fillna_value: Any,
    ) -> None:
        # If no new col is named to hold transformations,
        # then the transformations should be in-place.
        if not transformed_col:
            print(
                "WARNING: transformed_col name not supplied, transformations will be applied in-place."
            )
            transformed_col = target_col
        df[transformed_col] = df[target_col].fillna(fillna_value)

    def convert_csv_to_rdf(self) -> None:
        """
        Subtask RDF.2
        """
        tic = time.perf_counter()

        # Add some subclasses
        self.graph.add(
            (self.namespace.Restaurant, RDFS.subClassOf, self.namespace.Location)
        )
        self.graph.add((self.namespace.Location, RDFS.subClassOf, self.namespace.Place))
        self.graph.add((self.namespace.City, RDFS.subClassOf, self.namespace.Place))
        self.graph.add((self.namespace.Country, RDFS.subClassOf, self.namespace.Place))

        if "country" in self.data_df:
            self.mapping_to_create_type_triple(
                subject_col="country", class_type=self.namespace.Country
            )

            self.mapping_to_create_literal_triple(
                subject_col="country",
                object_col="country",
                predicate=self.namespace.name,
                datatype=RDF.PlainLiteral,
            )

        if "currency" in self.data_df:
            self.mapping_to_create_type_triple(
                subject_col="currency", class_type=self.namespace.Currency
            )

            self.mapping_to_create_literal_triple(
                subject_col="currency",
                object_col="currency",
                predicate=self.namespace.name,
                datatype=RDF.PlainLiteral,
            )

            self.mapping_to_create_object_triple(
                subject_col="currency",
                object_col="country",
                predicate=self.namespace.isCurrencyOf,
            )

        if "city" in self.data_df:

            self.mapping_to_create_type_triple(
                subject_col="city", class_type=self.namespace.City
            )

            self.mapping_to_create_literal_triple(
                subject_col="city",
                object_col="city",
                predicate=self.namespace.name,
                datatype=RDF.PlainLiteral,
            )

        if "name" in self.data_df:
            # TODO: preprocessing
            self.apply_preprocessing(
                df=self.data_df, target_col="name", transformed_col="cleaned_name"
            )

            # We give subject column and target type
            self.mapping_to_create_type_triple(
                subject_col="cleaned_name", class_type=self.namespace.Restaurant
            )

            self.mapping_to_create_literal_triple(
                subject_col="cleaned_name",
                object_col="name",
                predicate=self.namespace.name,
                datatype=RDF.PlainLiteral,
            )

            # TODO: Check if using RDF.PlainLiteral here is correct
            # Instead of XSD: primitive datatypes
            if "address" in self.data_df:
                self.mapping_to_create_literal_triple(
                    subject_col="cleaned_name",
                    object_col="address",
                    predicate=self.namespace.address,
                    datatype=RDF.PlainLiteral,
                )

            if "postcode" in self.data_df:
                self.mapping_to_create_literal_triple(
                    subject_col="cleaned_name",
                    object_col="postcode",
                    predicate=self.namespace.postcode,
                    datatype=XSD.string,
                )

            if "state" in self.data_df:
                self.mapping_to_create_literal_triple(
                    subject_col="cleaned_name",
                    object_col="state",
                    predicate=self.namespace.state,
                    datatype=XSD.string,
                )

            if "categories" in self.data_df:
                self.mapping_to_create_literal_triple(
                    subject_col="cleaned_name",
                    object_col="categories",
                    predicate=self.namespace.categories,
                    datatype=RDF.PlainLiteral,
                )

            self.mapping_to_create_object_triple(
                subject_col="cleaned_name",
                object_col="city",
                predicate=self.namespace.isPlaceInCity,
            )

            self.mapping_to_create_object_triple(
                subject_col="city",
                object_col="country",
                predicate=self.namespace.isPlaceInCountry,
            )

        if "name" in self.data_df and "menu item" in self.data_df:
            # Tidy weird characters from menu item column first
            self.apply_preprocessing(
                df=self.data_df,
                target_col="menu item",
                transformed_col="cleaned_menu_item",
            )

            # Make each item unique to the restaurant
            self.data_df["restaurant_name_menu_item"] = self.data_df[
                "cleaned_name"
            ].str.cat(self.data_df["cleaned_menu_item"], " ")

            # Create the menu item
            self.mapping_to_create_type_triple(
                subject_col="restaurant_name_menu_item",
                class_type=self.namespace.MenuItem,
            )

            self.mapping_to_create_object_triple(
                subject_col="restaurant_name_menu_item",
                object_col="cleaned_name",
                predicate=self.namespace.isMenuItemAt,
            )

            self.mapping_to_create_literal_triple(
                subject_col="restaurant_name_menu_item",
                object_col="cleaned_menu_item",
                predicate=self.namespace.name,
                datatype=RDF.PlainLiteral,
            )

            self.mapping_to_create_literal_triple(
                subject_col="restaurant_name_menu_item",
                object_col="item value",
                predicate=self.namespace.menu_item_price,
                datatype=XSD.decimal,
            )

            self.mapping_to_create_literal_triple(
                subject_col="restaurant_name_menu_item",
                object_col="currency",
                predicate=self.namespace.menu_item_price_currency,
                datatype=RDF.PlainLiteral,
            )

            self.mapping_to_create_literal_triple(
                subject_col="restaurant_name_menu_item",
                object_col="item description",
                predicate=self.namespace.menu_item_description,
                datatype=RDF.PlainLiteral,
            )

            toc = time.perf_counter()
            print(f"Finished in {toc - tic} seconds.")
            print(f"Extracted {len(self.graph)} triples.")

    @staticmethod
    def is_object_missing(value: str):
        """
        First is a check for NaN when the subject value
        could be a string (so can't use math.isnan())
        """
        return (value != value) or (value is None) or (value == "")

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
        TODO: Mapping to create triples like lab6:London rdf:type lab6:City
        A mapping may create more than one triple
        column: columns where the entity information is stored
        TODO: useExternalURI: if URI is fresh or from external KG
        """
        for subject in self.data_df[subject_col]:
            if self.is_object_missing(subject):
                return
            else:
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
        self,
        subject_col: str,
        object_col: str,
        predicate: rdflib.term.URIRef,
        datatype: str,
    ) -> None:
        """
        TODO: Mappings to create triples of the form lab6:london lab6:name "London"
        """
        for subject, lit_value in zip(
            self.data_df[subject_col], self.data_df[object_col]
        ):

            # Make sure this does nothing when the object is missing
            if self.is_object_missing(value=lit_value):
                return

            else:
                subject = subject.lower()
                # Use already created URI
                entity_uri = self.string_to_uri[subject]

                # Literal
                literal = Literal(lit_value, datatype=datatype)

                # Add new literal triple to graph
                self.graph.add((URIRef(entity_uri), predicate, literal))

    def mapping_to_create_object_triple(
        self, subject_col: str, object_col: str, predicate: rdflib.term.URIRef
    ) -> None:
        """
        Mappings to create triples of the form fp:Bend fp:isLocatedInCountry fp:USA
        """
        for subject, object in zip(self.data_df[subject_col], self.data_df[object_col]):
            # Make sure this does nothing when the object is missing
            if self.is_object_missing(value=subject) or self.is_object_missing(
                value=object
            ):
                return

            else:
                # Use already created URI
                subject_uri = self.string_to_uri[subject.lower()]
                object_uri = self.string_to_uri[object.lower()]

                # New triple
                self.graph.add((URIRef(subject_uri), predicate, URIRef(object_uri)))

    def debug(self):
        pprint(vars(self))

    def print(self, nrows: int = None):
        if not nrows:
            nrows = len(self.graph)

        for s, p, o in self.graph[:nrows]:
            print((s.n3(), p.n3(), o.n3()))
        print(f"Printed {len(self.graph)} triples.")

    def save_graph(self, output_file: str) -> None:
        # TODO: check what the first line does
        # print(self.g.serialize(format="turtle").decode("utf-8"))
        self.graph.serialize(destination=output_file, format="ttl")


if __name__ == "__main__":
    INPUT_FILEPATH = "../data/INM713_coursework_data_pizza_8358_1_reduced.csv"
    # INPUT_FILEPATH = "../data/data_pizza_spike.csv"
    NAMESPACE = Namespace("http://www.city.ac.uk/ds/inm713/feiphoon#")
    PREFIX = "fp"

    tab_to_graph = TabToGraph(
        input_filepath=INPUT_FILEPATH, namespace_str=NAMESPACE, prefix=PREFIX
    )

    tab_to_graph.convert_csv_to_rdf()

    # tab_to_graph.debug()
    # tab_to_graph.print()

    # Graph with only data
    tab_to_graph.save_graph(output_file="pizza_restaurants.ttl")

    # # OWL 2 RL reasoning
    # solution.performReasoning("ontology_lab6.ttl")  ##ttl format
    # # solution.performReasoning("ontology_lab6.owl") ##owl (rdf/xml) format

    # # Graph with ontology triples and entailed triples
    # solution.saveGraph(file.replace(".csv", "-" + task) + "-reasoning.ttl")

    # # SPARQL results into CSV
    # solution.performSPARQLQuery(file.replace(".csv", "-" + task) + "-query-results.csv")

    # # SPARQL for Lab 7
    # solution.performSPARQLQueryLab7()
