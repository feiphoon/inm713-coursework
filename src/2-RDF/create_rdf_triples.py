"""
Based heavily on code for lab6 of INM713.
Created on 05 March 2021
@author: ejimenez-ruiz
"""
from rdflib import Graph, Namespace
import pandas as pd

# import typing

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

    def convert_csv_to_rdf(self) -> None:
        pass

    def debug(self):
        pprint(vars(self))


if __name__ == "__main__":
    INPUT_FILEPATH = "../data/INM713_coursework_data_pizza_8358_1_reduced.csv"
    NAMESPACE = Namespace("http://www.city.ac.uk/ds/inm713/feiphoon#")
    PREFIX = "fp"

    tab_to_graph = TabToGraph(
        input_filepath=INPUT_FILEPATH, namespace_str=NAMESPACE, prefix=PREFIX
    )

    tab_to_graph.debug()
