"""
Based heavily on code for lab6 of INM713.
Created on 05 March 2021
@author: ejimenez-ruiz
"""
import rdflib
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, XSD, RDFS
from rdflib.util import guess_format
import owlrl

import re
import time
import pandas as pd
from pandas.core.frame import DataFrame
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
        self.data_df: pd.DataFrame = pd.read_csv(
            input_filepath, sep=",", quotechar='"', escapechar="\\", encoding="utf-8"
        )

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

    @staticmethod
    def clean_swapped_pizza(menu_item_name: str) -> None:
        menu_item_name = menu_item_name.lower()
        swapped_pizza_pattern = re.compile(r"^pizza\s?,\s?[a-z\s]+.$")
        # Matches `pizza, something asdjhgas asjdhgasd`

        if re.search(swapped_pizza_pattern, menu_item_name):

            match = re.search(swapped_pizza_pattern, menu_item_name)
            result = " ".join(list(map(str.strip, match.group(0).split(",")))[::-1])
            return result
        else:
            return menu_item_name

    def convert_csv_to_rdf(self) -> None:
        """
        Subtask RDF.2
        """
        tic = time.perf_counter()

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

        if "state" in self.data_df:
            # TODO: Great candidate for cleaning/lexical similarities

            self.mapping_to_create_type_triple(
                subject_col="state", class_type=self.namespace.State
            )

            self.mapping_to_create_literal_triple(
                subject_col="state",
                object_col="state",
                predicate=self.namespace.name,
                datatype=RDF.PlainLiteral,
            )

        # supposed to be Location
        # if "address" in self.data_df:

        #     self.mapping_to_create_type_triple(
        #         subject_col="state", class_type=self.namespace.State
        #     )

        #     self.mapping_to_create_literal_triple(
        #         subject_col="state",
        #         object_col="state",
        #         predicate=self.namespace.name,
        #         datatype=RDF.PlainLiteral,
        #     )

        if "name" in self.data_df:
            self.apply_preprocessing(
                df=self.data_df, target_col="name", transformed_col="cleaned_name"
            )

        if "address" in self.data_df:
            # Create a new complete_address column
            # While multiple locations could have the same restaurant name,
            # multiple restaurant names could be at the same location.
            _address_parts_cols = [
                "cleaned_name",
                "address",
                "city",
                "state",
                "postcode",
                "country",
            ]
            self.data_df["complete_address"] = self.data_df[_address_parts_cols].apply(
                lambda row: " ".join(row.values.astype(str)), axis=1
            )

            # Can be used in future to do an address lookup :)
            self.mapping_to_create_type_triple(
                subject_col="complete_address", class_type=self.namespace.Location
            )

            self.mapping_to_create_literal_triple(
                subject_col="complete_address",
                object_col="address",
                predicate=self.namespace.address,
                datatype=RDF.PlainLiteral,
            )

            self.mapping_to_create_literal_triple(
                subject_col="complete_address",
                object_col="city",
                predicate=self.namespace.city,
                datatype=RDF.PlainLiteral,
            )

            self.mapping_to_create_literal_triple(
                subject_col="complete_address",
                object_col="state",
                predicate=self.namespace.state,
                datatype=XSD.string,
            )

            self.mapping_to_create_literal_triple(
                subject_col="complete_address",
                object_col="postcode",
                predicate=self.namespace.postcode,
                datatype=XSD.string,
            )

            self.mapping_to_create_literal_triple(
                subject_col="complete_address",
                object_col="country",
                predicate=self.namespace.country,
                datatype=RDF.PlainLiteral,
            )

            self.mapping_to_create_literal_triple(
                subject_col="complete_address",
                object_col="categories",
                predicate=self.namespace.categories,
                datatype=XSD.string,
            )

        if (
            ("name" in self.data_df)
            and ("cleaned_name" in self.data_df)
            and ("complete_address" in self.data_df)
        ):
            self.mapping_to_create_type_triple(
                subject_col="cleaned_name", class_type=self.namespace.Restaurant
            )

            self.mapping_to_create_object_triple(
                subject_col="cleaned_name",
                object_col="complete_address",
                predicate=self.namespace.hasLocation,
            )

            self.mapping_to_create_literal_triple(
                subject_col="cleaned_name",
                object_col="name",
                predicate=self.namespace.name,
                datatype=RDF.PlainLiteral,
            )

        if "cleaned_name" in self.data_df and "menu item" in self.data_df:
            # Tidy weird characters from menu item column first
            self.apply_preprocessing(
                df=self.data_df,
                target_col="menu item",
                transformed_col="cleaned_menu_item",
            )

            # Special cleaning for Pizza items
            self.data_df["cleaned_menu_item"] = self.data_df["cleaned_menu_item"].apply(
                lambda row: self.clean_swapped_pizza(row)
            )

            # Make each item unique to the location
            self.data_df["location_menu_item"] = self.data_df[
                "complete_address"
            ].str.cat(self.data_df["cleaned_menu_item"], " ")

            # Create the menu item
            self.mapping_to_create_type_triple(
                subject_col="location_menu_item",
                class_type=self.namespace.MenuItem,
            )

            self.mapping_to_create_literal_triple(
                subject_col="location_menu_item",
                object_col="cleaned_menu_item",
                predicate=self.namespace.name,
                datatype=RDF.PlainLiteral,
            )

            self.mapping_to_create_literal_triple(
                subject_col="location_menu_item",
                object_col="item value",
                predicate=self.namespace.menu_item_price,
                datatype=XSD.decimal,
            )

            self.mapping_to_create_literal_triple(
                subject_col="location_menu_item",
                object_col="currency",
                predicate=self.namespace.menu_item_price_currency,
                datatype=RDF.PlainLiteral,
            )

            self.mapping_to_create_literal_triple(
                subject_col="location_menu_item",
                object_col="item description",
                predicate=self.namespace.menu_item_description,
                datatype=RDF.PlainLiteral,
            )

        if ("location_menu_item" in self.data_df) and (
            "complete_address" in self.data_df
        ):
            # Place menu items at a Location using isMenuItemAt
            self.mapping_to_create_object_triple(
                subject_col="location_menu_item",
                object_col="complete_address",
                predicate=self.namespace.isMenuItemAt,
            )

        # Then let's pick out our Known Pizza types
        if ("cleaned_menu_item" in self.data_df) and (
            "location_menu_item" in self.data_df
        ):
            self.mapping_to_create_pizza_bianca_type_triple(
                subject_col="location_menu_item",
                conditional_col="cleaned_menu_item",
                class_type=self.namespace.PizzaBianca,
            )

            self.mapping_to_create_pizza_margherita_type_triple(
                subject_col="location_menu_item",
                conditional_col="cleaned_menu_item",
                class_type=self.namespace.PizzaMargherita,
            )

        toc = time.perf_counter()
        print(f"Finished converting CSV to RDF in {toc - tic} seconds.")
        print(f"Extracted {len(self.graph)} triples.")

    def mapping_to_create_pizza_bianca_type_triple(
        self, subject_col: str, conditional_col: str, class_type: rdflib.term.URIRef
    ) -> None:
        for subject, conditional in zip(
            self.data_df[subject_col], self.data_df[conditional_col]
        ):
            if self.is_object_missing(subject) or self.is_object_missing(conditional):
                return
            else:
                conditional = conditional.lower()
                subject = subject.lower()

                # Pizza Bianca conditions
                if (conditional == "pizza bianca") or (conditional == "white pizza"):
                    entity_uri: str = None

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

    def mapping_to_create_pizza_margherita_type_triple(
        self, subject_col: str, conditional_col: str, class_type: rdflib.term.URIRef
    ) -> None:
        for subject, conditional in zip(
            self.data_df[subject_col], self.data_df[conditional_col]
        ):
            if self.is_object_missing(subject) or self.is_object_missing(conditional):
                return
            else:
                conditional = conditional.lower()
                subject = subject.lower()

                # Pizza Bianca conditions
                if "margherita" in conditional:
                    entity_uri: str = None

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
                entity_uri: str = None
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

    def perform_reasoning(self, ontology_file: str) -> None:
        """
        Subtask SPARQL.1
        Expand the graph with the inferred triples, using reasoning.
        """
        # print(guess_format(ontology_file))
        self.graph.load(ontology_file, format=guess_format(ontology_file))

        print(f"Triples including ontology: {len(self.graph)}.")

        # Happy with this reasoner
        owlrl.DeductiveClosure(
            owlrl.OWLRL.OWLRL_Semantics,
            axiomatic_triples=False,
            datatype_axioms=False,
        ).expand(self.graph)

        print(f"Triples after OWL 2 RL reasoning: {len(self.graph)}.")

    def debug(self) -> None:
        pprint(vars(self))

    def display(self, nrows: int = None) -> None:
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
    # INPUT_FILEPATH: str = "../../data/INM713_coursework_data_pizza_8358_1_reduced.csv"
    # INPUT_FILEPATH = "../../data/data_pizza_preprocessing_test.csv"
    # INPUT_FILEPATH = "../../data/data_pizza_shared_restaurant_name_test.csv"
    # INPUT_FILEPATH = "../../data/data_pizza_bianca_white_test.csv"
    INPUT_FILEPATH = "../../data/data_pizza_margherita_test.csv"
    NAMESPACE: str = Namespace("http://www.city.ac.uk/ds/inm713/feiphoon#")
    PREFIX: str = "fp"

    tab_to_graph = TabToGraph(
        input_filepath=INPUT_FILEPATH, namespace_str=NAMESPACE, prefix=PREFIX
    )

    tab_to_graph.convert_csv_to_rdf()

    for s, p, o in tab_to_graph.graph:
        print((s.n3(), p.n3(), o.n3()))

    # Graph with only data
    # tab_to_graph.save_graph(output_file="pizza_restaurants_without_reasoning.ttl")

    # Apply OWL 2 RL reasoning
    # tab_to_graph.perform_reasoning(
    #     "../../1-OWL/pizza_restaurant_ontology6.ttl"
    # )  # ttl format
    # # tab_to_graph.perform_reasoning("../data/pizza_restaurant_ontology5-slim.owl") ##owl (rdf/xml) format

    # # Graph with ontology triples and entailed triples
    # tab_to_graph.save_graph("pizza_restaurants_with_reasoning.ttl")

    # # SPARQL results into CSV
    # solution.performSPARQLQuery(file.replace(".csv", "-" + task) + "-query-results.csv")

    # # SPARQL for Lab 7
    # solution.performSPARQLQueryLab7()
