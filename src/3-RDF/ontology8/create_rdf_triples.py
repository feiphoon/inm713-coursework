"""
Triples code based on lab6 of INM713.
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
        # self.data_df: pd.DataFrame = pd.read_csv(
        #     input_filepath, sep=",", quotechar='"', escapechar="\\", encoding="utf-8"
        # )
        self.data_df: pd.DataFrame = pd.read_csv(input_filepath, encoding="utf-8")
        self.data_df_len: int = len(self.data_df)

        EXPECTED_COLUMNS = [
            "name",
            "address",
            "city",
            "country",
            "postcode",
            "state",
            "categories",
            "menu item",
            "item value",
            "currency",
            "item description",
        ]
        self._validate_dataset(
            df=self.data_df, expected_columns=EXPECTED_COLUMNS, min_expected_len=1
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
    def _validate_dataset(
        df: DataFrame, expected_columns: list, min_expected_len: int
    ) -> Exception:
        if not (df.columns.isin(expected_columns).all()):
            raise Exception("Some expected columns are missing.")
        if not (len(df) >= min_expected_len):
            raise Exception("Dataset does not meet the minimum expected length.")

    @staticmethod
    def _apply_preprocessing(
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
        # Note: unidecode is buggy
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
    def _replace_missing_values(
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
    def _clean_swapped_pizza(menu_item_name: str) -> None:
        menu_item_name = menu_item_name.lower()

        # A pattern that matches `pizza, something asdjhgas asjdhgasd`
        swapped_pizza_pattern = re.compile(r"^pizza\s?,\s?[a-z\s]+.$")

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

        # Map Country
        self._mapping_to_create_type_triple(
            subject_col="country",
            class_type=self.namespace.Country,
            use_external_uri=use_external_uri,
            category_filter="http://dbpedia.org/resource/Category:Lists_of_countries",
        )

        self._mapping_to_create_literal_triple(
            subject_col="country",
            object_col="country",
            predicate=self.namespace.name,
            datatype=XSD.string,
        )

        # Map Currency
        self._mapping_to_create_type_triple(
            subject_col="currency",
            class_type=self.namespace.Currency,
        )

        self._mapping_to_create_literal_triple(
            subject_col="currency",
            object_col="currency",
            predicate=self.namespace.name,
            datatype=XSD.string,
        )

        self._mapping_to_create_object_triple(
            subject_col="currency",
            object_col="country",
            predicate=self.namespace.isCurrencyOf,
        )

        # Map City
        self._mapping_to_create_type_triple(
            subject_col="city",
            class_type=self.namespace.City,
            use_external_uri=use_external_uri,
            category_filter="http://dbpedia.org/resource/Category:Cities_in_the_United_States",
        )

        self._mapping_to_create_literal_triple(
            subject_col="city",
            object_col="city",
            predicate=self.namespace.name,
            datatype=XSD.string,
        )

        # Map State
        self._mapping_to_create_type_triple(
            subject_col="state",
            class_type=self.namespace.State,
            use_external_uri=use_external_uri,
            category_filter="http://dbpedia.org/resource/Category:States_of_the_United_States",
        )

        self._mapping_to_create_literal_triple(
            subject_col="state",
            object_col="state",
            predicate=self.namespace.name,
            datatype=XSD.string,
        )

        # Preprocess name
        self._apply_preprocessing(
            df=self.data_df, target_col="name", transformed_col="cleaned_name"
        )

        # Preprocess postcode
        self._replace_missing_values(
            df=self.data_df,
            target_col="postcode",
            transformed_col="cleaned_postcode",
            fillna_value=" ",
        )

        # Build a complete name of each Restaurant based on their name and full address
        if ("cleaned_postcode" in self.data_df) and ("cleaned_name" in self.data_df):
            # Addresses a very specific bug in postcode type being inferred as float.
            self.data_df["cleaned_postcode"] = self.data_df["cleaned_postcode"].astype(
                str
            )
            self.data_df["cleaned_postcode"] = self.data_df[
                "cleaned_postcode"
            ].str.replace(r".0$", "", regex=True)

            # Create a new complete_address column
            # While multiple locations could have the same restaurant name,
            # multiple restaurant names could be at the same location.
            _address_parts_cols = [
                "cleaned_name",
                "address",
                "city",
                "state",
                "cleaned_postcode",
                "country",
            ]
            self.data_df["complete_address"] = self.data_df[_address_parts_cols].apply(
                lambda row: " ".join(row.values.astype(str)), axis=1
            )

            self.data_df["complete_address"] = self.data_df[
                "complete_address"
            ].str.replace("-", "_")

            self._mapping_to_create_type_triple(
                subject_col="complete_address", class_type=self.namespace.Restaurant
            )

            self._mapping_to_create_literal_triple(
                subject_col="complete_address",
                object_col="name",
                predicate=self.namespace.name,
                datatype=XSD.string,
            )

            self._mapping_to_create_literal_triple(
                subject_col="complete_address",
                object_col="address",
                predicate=self.namespace.address,
                datatype=XSD.string,
            )

            self._mapping_to_create_literal_triple(
                subject_col="complete_address",
                object_col="city",
                predicate=self.namespace.city,
                datatype=XSD.string,
            )

            self._mapping_to_create_literal_triple(
                subject_col="complete_address",
                object_col="state",
                predicate=self.namespace.state,
                datatype=XSD.string,
            )

            self._mapping_to_create_literal_triple(
                subject_col="complete_address",
                object_col="cleaned_postcode",
                predicate=self.namespace.postcode,
                datatype=XSD.string,
            )

            self._mapping_to_create_literal_triple(
                subject_col="complete_address",
                object_col="country",
                predicate=self.namespace.country,
                datatype=XSD.string,
            )

            self._mapping_to_create_literal_triple(
                subject_col="complete_address",
                object_col="categories",
                predicate=self.namespace.categories,
                datatype=XSD.string,
            )

            self._mapping_to_create_object_triple(
                subject_col="complete_address",
                object_col="city",
                predicate=self.namespace.isPlaceInCity,
            )

            self._mapping_to_create_object_triple(
                subject_col="complete_address",
                object_col="state",
                predicate=self.namespace.isPlaceInState,
            )

            self._mapping_to_create_object_triple(
                subject_col="complete_address",
                object_col="country",
                predicate=self.namespace.isPlaceInCountry,
            )

        # Preprocess menu item
        # Tidy weird characters from menu item column first
        self._apply_preprocessing(
            df=self.data_df,
            target_col="menu item",
            transformed_col="cleaned_menu_item",
        )

        # Special cleaning for Pizza items
        self.data_df["cleaned_menu_item"] = self.data_df["cleaned_menu_item"].apply(
            lambda row: self._clean_swapped_pizza(row)
        )

        # Deal with nulls in data related to menu items
        # Fill in nulls
        self._replace_missing_values(
            df=self.data_df,
            target_col="item value",
            transformed_col="menu_item_price",
            fillna_value=0.0,
        )

        self._replace_missing_values(
            df=self.data_df,
            target_col="currency",
            transformed_col="menu_item_price_currency",
            fillna_value=" ",
        )

        self._replace_missing_values(
            df=self.data_df,
            target_col="item description",
            transformed_col="menu_item_description",
            fillna_value=" ",
        )

        # Now complete the menu item name
        if self.data_df.columns.isin(
            [
                "complete_address",
                "cleaned_menu_item",
                "menu_item_price",
                "menu_item_price_currency",
                "menu_item_description",
            ]
        ).any():

            # Make each item unique to the restaurant
            self.data_df["restaurant_menu_item"] = self.data_df[
                "complete_address"
            ].str.cat(self.data_df["cleaned_menu_item"], " ")

            # Create the menu item
            self._mapping_to_create_type_triple(
                subject_col="restaurant_menu_item",
                class_type=self.namespace.MenuItem,
            )

            self._mapping_to_create_literal_triple(
                subject_col="restaurant_menu_item",
                object_col="cleaned_menu_item",
                predicate=self.namespace.name,
                datatype=XSD.string,
            )

            self._mapping_to_create_literal_triple(
                subject_col="restaurant_menu_item",
                object_col="menu_item_price",
                predicate=self.namespace.menu_item_price,
                datatype=XSD.float,
            )

            self._mapping_to_create_literal_triple(
                subject_col="restaurant_menu_item",
                object_col="menu_item_price_currency",
                predicate=self.namespace.menu_item_price_currency,
                datatype=XSD.string,
            )

            self._mapping_to_create_literal_triple(
                subject_col="restaurant_menu_item",
                object_col="menu_item_description",
                predicate=self.namespace.menu_item_description,
                datatype=XSD.string,
            )

            # Place menu items at a Restaurant using isMenuItemAt
            self._mapping_to_create_object_triple(
                subject_col="restaurant_menu_item",
                object_col="complete_address",
                predicate=self.namespace.isMenuItemAt,
            )

        if ("cleaned_menu_item" in self.data_df) and (
            "restaurant_menu_item" in self.data_df
        ):
            # Make all menu items Pizza type
            # It may not be true, but that's another
            # whole preprocessing issue.
            self._mapping_to_create_type_triple(
                subject_col="restaurant_menu_item", class_type=self.namespace.Pizza
            )

            # Then let's pick out our Known Pizzas
            self._mapping_to_create_pizza_bianca_type_triple(
                subject_col="restaurant_menu_item",
                conditional_col="cleaned_menu_item",
                class_type=self.namespace.Bianca,
            )

            self._mapping_to_create_pizza_margherita_type_triple(
                subject_col="restaurant_menu_item",
                conditional_col="cleaned_menu_item",
                class_type=self.namespace.Margherita,
            )

            self._mapping_to_create_pizza_sicilian_type_triple(
                subject_col="restaurant_menu_item",
                conditional_col="cleaned_menu_item",
                class_type=self.namespace.Sicilian,
            )

            self._mapping_to_create_pizza_seafood_type_triple(
                subject_col="restaurant_menu_item",
                conditional_col="cleaned_menu_item",
                class_type=self.namespace.Seafood,
            )

            self._mapping_to_create_pizza_four_cheese_type_triple(
                subject_col="restaurant_menu_item",
                conditional_col="cleaned_menu_item",
                class_type=self.namespace.FourCheese,
            )

        toc = time.perf_counter()
        print(f"Finished converting CSV to RDF in {toc - tic} seconds.")
        print(f"Extracted {len(self.graph)} triples.")

    def _mapping_to_create_pizza_bianca_type_triple(
        self, subject_col: str, conditional_col: str, class_type: rdflib.term.URIRef
    ) -> None:
        for subject, conditional in zip(
            self.data_df[subject_col], self.data_df[conditional_col]
        ):
            if self._is_object_missing(subject) or self._is_object_missing(conditional):
                pass
            else:
                conditional = conditional.lower()
                subject = subject.lower()

                # Pizza Bianca conditions - crude and would have been a nice
                # opportunity to look at labels in different languages -
                # but Italian is not provided as an option.
                if ("bianca" in conditional) or (conditional == "white pizza"):
                    entity_uri: str = None

                    if subject in self.string_to_uri:
                        entity_uri = self.string_to_uri[subject]
                    else:
                        entity_uri = self._createURIForEntity(subject)

                    self.graph.add((URIRef(entity_uri), RDF.type, class_type))

    def _mapping_to_create_pizza_margherita_type_triple(
        self, subject_col: str, conditional_col: str, class_type: rdflib.term.URIRef
    ) -> None:
        for subject, conditional in zip(
            self.data_df[subject_col], self.data_df[conditional_col]
        ):
            if self._is_object_missing(subject) or self._is_object_missing(conditional):
                pass
            else:
                conditional = conditional.lower()
                subject = subject.lower()

                # Pizza Bianca conditions - crude and chose not to use better matching here
                if "margherita" in conditional or "margarita" in conditional:
                    entity_uri: str = None

                    if subject in self.string_to_uri:
                        entity_uri = self.string_to_uri[subject]
                    else:
                        entity_uri = self._createURIForEntity(subject)

                    self.graph.add((URIRef(entity_uri), RDF.type, class_type))

    def _mapping_to_create_pizza_sicilian_type_triple(
        self, subject_col: str, conditional_col: str, class_type: rdflib.term.URIRef
    ) -> None:
        for subject, conditional in zip(
            self.data_df[subject_col], self.data_df[conditional_col]
        ):
            if self._is_object_missing(subject) or self._is_object_missing(conditional):
                pass
            else:
                conditional = conditional.lower()
                subject = subject.lower()

                # Sicilian conditions - crude and chose not to use better matching here
                if "sicilian" in conditional:
                    entity_uri: str = None

                    if subject in self.string_to_uri:
                        entity_uri = self.string_to_uri[subject]
                    else:
                        entity_uri = self._createURIForEntity(subject)

                    self.graph.add((URIRef(entity_uri), RDF.type, class_type))

    def _mapping_to_create_pizza_seafood_type_triple(
        self, subject_col: str, conditional_col: str, class_type: rdflib.term.URIRef
    ) -> None:
        for subject, conditional in zip(
            self.data_df[subject_col], self.data_df[conditional_col]
        ):
            if self._is_object_missing(subject) or self._is_object_missing(conditional):
                pass
            else:
                conditional = conditional.lower()
                subject = subject.lower()

                # Seafood conditions - crude and chose not to use better matching here
                if "seafood" in conditional:
                    entity_uri: str = None

                    if subject in self.string_to_uri:
                        entity_uri = self.string_to_uri[subject]
                    else:
                        entity_uri = self._createURIForEntity(subject)

                    self.graph.add((URIRef(entity_uri), RDF.type, class_type))

    def _mapping_to_create_pizza_four_cheese_type_triple(
        self, subject_col: str, conditional_col: str, class_type: rdflib.term.URIRef
    ) -> None:
        for subject, conditional in zip(
            self.data_df[subject_col], self.data_df[conditional_col]
        ):
            if self._is_object_missing(subject) or self._is_object_missing(conditional):
                pass
            else:
                conditional = conditional.lower()
                subject = subject.lower()

                # Four cheese conditions - crude and chose not to use better matching here
                if (conditional == "4 cheese pizza") or (
                    conditional == "four cheese pizza"
                ):
                    entity_uri: str = None

                    if subject in self.string_to_uri:
                        entity_uri = self.string_to_uri[subject]
                    else:
                        entity_uri = self._createURIForEntity(subject)

                    self.graph.add((URIRef(entity_uri), RDF.type, class_type))

    def _mapping_to_create_pizza_cheese_type_triple(
        self, subject_col: str, conditional_col: str, class_type: rdflib.term.URIRef
    ) -> None:
        for subject, conditional in zip(
            self.data_df[subject_col], self.data_df[conditional_col]
        ):
            if self._is_object_missing(subject) or self._is_object_missing(conditional):
                pass
            else:
                conditional = conditional.lower()
                subject = subject.lower()

                # Cheese conditions - crude and chose not to use better matching here
                if conditional == "cheese pizza":
                    entity_uri: str = None

                    if subject in self.string_to_uri:
                        entity_uri = self.string_to_uri[subject]
                    else:
                        entity_uri = self._createURIForEntity(subject)

                    self.graph.add((URIRef(entity_uri), RDF.type, class_type))

    @staticmethod
    def _is_object_missing(value: str) -> bool:
        """
        First is a check for NaN when the subject value
        could be a string (so can't use math.isnan())
        """
        return (value != value) or (value is None) or (value == "")

    def _get_external_kg_uri(self, name: str, category_filter: str = "") -> None:
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

    def _createURIForEntity(
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
            uri = self._get_external_kg_uri(
                name=entity_name, category_filter=category_filter
            )
            if uri != "":
                self.string_to_uri[entity_name] = uri

        return self.string_to_uri[entity_name]

    def _mapping_to_create_type_triple(
        self,
        subject_col: str,
        class_type: rdflib.term.URIRef,
        use_external_uri: bool = False,
        category_filter: str = "",
    ) -> None:
        """
        Mapping to create triples like fp:MenuItem rdf:type fp:Pizza.
        """
        for subject in self.data_df[subject_col]:
            if self._is_object_missing(value=subject):
                return
            else:
                entity_uri: str = None
                subject = subject.lower()

                if subject in self.string_to_uri:
                    entity_uri = self.string_to_uri[subject]
                else:
                    entity_uri = self._createURIForEntity(
                        entity_name=subject,
                        use_external_uri=use_external_uri,
                        category_filter=category_filter,
                    )

                self.graph.add((URIRef(entity_uri), RDF.type, class_type))

    def _mapping_to_create_literal_triple(
        self,
        subject_col: str,
        object_col: str,
        predicate: rdflib.term.URIRef,
        datatype: str,
    ) -> None:
        """
        Mapping to create triples of the form fp:Restaurant fp:name "Nonna's Pizza"^^datatype
        """
        for subject, lit_value in zip(
            self.data_df[subject_col], self.data_df[object_col]
        ):

            # Make sure this does nothing when the object is missing
            if self._is_object_missing(value=lit_value):
                return

            else:
                subject = subject.lower()
                # Use already created URI
                entity_uri = self.string_to_uri[subject]

                # Literal
                literal = Literal(lit_value, datatype=datatype)

                # Add new literal triple to graph
                self.graph.add((URIRef(entity_uri), predicate, literal))

    def _mapping_to_create_object_triple(
        self, subject_col: str, object_col: str, predicate: rdflib.term.URIRef
    ) -> None:
        """
        Mappings to create triples of the form fp:cheese_pizza fp:isMenuItemAt fp:Restaurant
        """
        for subject, object in zip(self.data_df[subject_col], self.data_df[object_col]):

            # Make sure this does nothing when the object is missing
            if self._is_object_missing(value=subject) or self._is_object_missing(
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

    def display(self) -> None:
        for s, p, o in self.graph:
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
    # INPUT_FILEPATH = "../../data/data_pizza_no_postcode_test.csv"

    NAMESPACE_STR: str = "http://www.city.ac.uk/ds/inm713/feiphoon#"
    PREFIX: str = "fp"

    tab_to_graph = TabToGraph(
        input_filepath=INPUT_FILEPATH, namespace_str=NAMESPACE_STR, prefix=PREFIX
    )

    # Comment these out to run each task
    TASK: Task = Task.RDF2
    TASK: Task = Task.RDF3
    TASK: Task = Task.SPARQL1

    if TASK == Task.RDF2:
        tab_to_graph.convert_csv_to_rdf(use_external_uri=False)
        tab_to_graph.save_graph(
            output_file=f"pizza_restaurants_without_reasoning_{TASK.value}.ttl"
        )

    elif TASK == Task.RDF3:
        tab_to_graph.convert_csv_to_rdf(use_external_uri=True)
        tab_to_graph.save_graph(
            output_file=f"pizza_restaurants_without_reasoning_{TASK.value}.ttl"
        )

    if TASK == Task.SPARQL1:
        tab_to_graph.convert_csv_to_rdf(use_external_uri=True)

        # Apply OWL 2 RL reasoning
        tab_to_graph.perform_reasoning(
            "../../2-OWL/pizza_restaurant_ontology8.ttl"
        )  # ttl format
        # tab_to_graph.perform_reasoning("../../2-OWL/pizza_restaurant_ontology8.owl") ##owl (rdf/xml) format

        # Graph with ontology triples and entailed triples
        tab_to_graph.save_graph(
            output_file=f"pizza_restaurants_with_reasoning_{TASK.value}.ttl"
        )
