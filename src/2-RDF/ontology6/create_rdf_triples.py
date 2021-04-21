"""
Based heavily on code for lab6 of INM713.
Created on 05 March 2021
@author: ejimenez-ruiz

Subtask RDF.2
Subtask RDF.3
Subtask SPARQL.1
"""
import rdflib
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, XSD
from rdflib.util import guess_format
import owlrl

from lookup import DBpediaLookup, WikidataAPI, GoogleKGLookup
from stringcmp import isub

from enum import Enum
import re
import time
import pandas as pd
from pandas.core.frame import DataFrame
from unidecode import unidecode

from typing import Dict, Optional, Any
from pprint import pprint


class Task(Enum):
    RDF2 = "rdf2"
    RDF3 = "rdf3"
    SPARQL1 = "sparql1"


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
        self.data_df: pd.DataFrame = pd.read_csv(
            input_filepath, sep=",", quotechar='"', escapechar="\\", encoding="utf-8"
        )

        # Dictionary to store URIs
        self.string_to_uri: dict = {}

        # Enable DBPedia lookups
        self.dbpedia = DBpediaLookup()

        # Enable Wikidata lookups
        self.wikidata = WikidataAPI()

        # Enable GoogleKG lookups
        self.googlekg = GoogleKGLookup()

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

    def convert_csv_to_rdf(self, use_external_uri: bool = False) -> None:
        """
        Subtask RDF.2
        Subtask RDF.3
        """
        tic = time.perf_counter()

        if "country" in self.data_df:
            self.mapping_to_create_type_triple(
                subject_col="country",
                class_type=self.namespace.Country,
                use_external_uri=use_external_uri,
                category_filter="http://dbpedia.org/resource/Category:Lists_of_countries",
            )

            self.mapping_to_create_literal_triple(
                subject_col="country",
                object_col="country",
                predicate=self.namespace.name,
                datatype=XSD.string,
            )

        if "currency" in self.data_df:
            self.mapping_to_create_type_triple(
                subject_col="currency",
                class_type=self.namespace.Currency,
            )

            self.mapping_to_create_literal_triple(
                subject_col="currency",
                object_col="currency",
                predicate=self.namespace.name,
                datatype=XSD.string,
            )

            self.mapping_to_create_object_triple(
                subject_col="currency",
                object_col="country",
                predicate=self.namespace.isCurrencyOf,
            )

        if "city" in self.data_df:
            self.mapping_to_create_type_triple(
                subject_col="city",
                class_type=self.namespace.City,
                use_external_uri=use_external_uri,
                category_filter="http://dbpedia.org/resource/Category:Cities_in_the_United_States",
            )

            self.mapping_to_create_literal_triple(
                subject_col="city",
                object_col="city",
                predicate=self.namespace.name,
                datatype=XSD.string,
            )

        if "state" in self.data_df:
            self.mapping_to_create_type_triple(
                subject_col="state",
                class_type=self.namespace.State,
                use_external_uri=use_external_uri,
                category_filter="http://dbpedia.org/resource/Category:States_of_the_United_States",
            )

            self.mapping_to_create_literal_triple(
                subject_col="state",
                object_col="state",
                predicate=self.namespace.name,
                datatype=XSD.string,
            )

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
                datatype=XSD.string,
            )

            self.mapping_to_create_literal_triple(
                subject_col="complete_address",
                object_col="city",
                predicate=self.namespace.city,
                datatype=XSD.string,
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
                datatype=XSD.string,
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
                datatype=XSD.string,
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
                datatype=XSD.string,
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
                datatype=XSD.string,
            )

            self.mapping_to_create_literal_triple(
                subject_col="location_menu_item",
                object_col="item description",
                predicate=self.namespace.menu_item_description,
                datatype=XSD.string,
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

        # Then let's pick out our Known Pizza
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
                if "margherita" in conditional or "margarita" in conditional:
                    entity_uri: str = None

                    if subject in self.string_to_uri:
                        entity_uri = self.string_to_uri[subject]
                    else:
                        entity_uri = self.createURIForEntity(subject)

                    self.graph.add((URIRef(entity_uri), RDF.type, class_type))

    @staticmethod
    def is_object_missing(value: str) -> bool:
        """
        First is a check for NaN when the subject value
        could be a string (so can't use math.isnan())
        """
        return (value != value) or (value is None) or (value == "")

    def get_external_kg_uri(self, name: str, category_filter: str = "") -> None:
        """
        Approximate solution: We get the entity with highest lexical similarity
        The use of context may be necessary in some cases
        """
        entities = self.dbpedia.getKGEntities(
            query=name, limit=5, category_filter=category_filter
        )
        # entities = self.wikidata.getKGEntities(name, 5)
        # entities = self.googlekg.getKGEntities(name, 5)
        current_sim = -1
        current_uri = ""
        if entities:
            for ent in entities:
                isub_score = isub(name, ent.label)
                if current_sim < isub_score:
                    current_uri = ent.ident
                    current_sim = isub_score

        return current_uri

    def createURIForEntity(
        self,
        entity_name: str,
        use_external_uri: bool = False,
        category_filter: str = "",
    ) -> Dict[str, str]:
        # We create fresh URI (default option)
        self.string_to_uri[entity_name] = self.namespace_str + entity_name.replace(
            " ", "_"
        )

        if use_external_uri:
            uri = self.get_external_kg_uri(
                name=entity_name, category_filter=category_filter
            )
            if uri != "":
                self.string_to_uri[entity_name] = uri

        return self.string_to_uri[entity_name]

    def mapping_to_create_type_triple(
        self,
        subject_col: str,
        class_type: rdflib.term.URIRef,
        use_external_uri: bool = False,
        category_filter: str = "",
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

                if subject in self.string_to_uri:
                    entity_uri = self.string_to_uri[subject]
                else:
                    entity_uri = self.createURIForEntity(
                        entity_name=subject,
                        use_external_uri=use_external_uri,
                        category_filter=category_filter,
                    )

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
        tic = time.perf_counter()
        # print(guess_format(ontology_file))
        self.graph.load(ontology_file, format=guess_format(ontology_file))

        print(f"Triples including ontology: {len(self.graph)}.")

        # Happy with this reasoner
        owlrl.DeductiveClosure(
            owlrl.OWLRL.OWLRL_Semantics,
            axiomatic_triples=False,
            datatype_axioms=False,
        ).expand(self.graph)

        toc = time.perf_counter()
        print(f"Finished reasoning on graph in {toc - tic} seconds.")
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
        # print(self.g.serialize(format="turtle").decode("utf-8"))
        self.graph.serialize(destination=output_file, format="ttl")


if __name__ == "__main__":
    INPUT_FILEPATH: str = "../../data/INM713_coursework_data_pizza_8358_1_reduced.csv"
    # INPUT_FILEPATH = "../../data/data_pizza_preprocessing_test.csv"
    # INPUT_FILEPATH = "../../data/data_pizza_shared_restaurant_name_test.csv"
    # INPUT_FILEPATH = "../../data/data_pizza_bianca_white_test.csv"
    # INPUT_FILEPATH = "../../data/data_pizza_margherita_test.csv"
    # INPUT_FILEPATH = "../../data/data_pizza_minimum_test.csv"

    NAMESPACE: str = Namespace("http://www.city.ac.uk/ds/inm713/feiphoon#")
    PREFIX: str = "fp"

    tab_to_graph = TabToGraph(
        input_filepath=INPUT_FILEPATH, namespace_str=NAMESPACE, prefix=PREFIX
    )

    # TASK: Task = Task.RDF2
    # TASK: Task = Task.RDF3
    TASK: Task = Task.SPARQL1

    if TASK == Task.RDF2:
        tab_to_graph.convert_csv_to_rdf(use_external_uri=False)
    elif TASK == Task.RDF3:
        tab_to_graph.convert_csv_to_rdf(use_external_uri=True)

    # Save graph with only data
    tab_to_graph.save_graph(
        output_file=f"pizza_restaurants_without_reasoning_{TASK.value}.ttl"
    )

    if TASK == Task.SPARQL1:
        tab_to_graph.convert_csv_to_rdf(use_external_uri=True)

        # Apply OWL 2 RL reasoning
        tab_to_graph.perform_reasoning(
            "../../1-OWL/pizza_restaurant_ontology6.ttl"
        )  # ttl format
        # tab_to_graph.perform_reasoning("../../1-OWL/pizza_restaurant_ontology6.owl") ##owl (rdf/xml) format

        # Graph with ontology triples and entailed triples
        tab_to_graph.save_graph(
            output_file=f"pizza_restaurants_with_reasoning_{TASK.value}.ttl"
        )

    # # SPARQL results into CSV
    # solution.performSPARQLQuery(file.replace(".csv", "-" + task) + "-query-results.csv")

    # # SPARQL for Lab 7
    # solution.performSPARQLQueryLab7()
