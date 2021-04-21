"""
Modification of code from INM713 labs

Created on 19 Jan 2021

@author: ejimenez-ruiz

Subtask SPARQL.2
Subtask SPARQL.3
Subtask SPARQL.4
Subtask SPARQL.5
Subtask SPARQL.6
"""
# from owlready2 import *
from rdflib import Graph
from rdflib.util import guess_format

from enum import Enum
from pprint import pprint


class Task(Enum):
    SPARQL2 = "sparql2"
    SPARQL3 = "sparql3"
    SPARQL4 = "sparql4"
    SPARQL5 = "sparql5"


# from rdflib.plugins.sparql import prepareQuery
# from SPARQLWrapper import SPARQLWrapper, JSON
# import requests


class PizzaRestaurantGraph:
    def __init__(self, filename: str) -> None:
        self.graph = Graph()
        self.graph.parse(filename, format=guess_format(filename))
        print(f"Loaded {len(self.graph)} triples.")

    def debug(self) -> None:
        pprint(vars(self))

    def display(self) -> None:
        for s, p, o in self.graph:
            print((s.n3(), p.n3(), o.n3()))
        print(f"Printed {len(self.graph)} triples.")

    def query_graph(
        self, query: str, output_filename: str = "", output_fields: list = []
    ) -> None:
        result = self.graph.query(query)

        print(f"Found {len(result)} results.")
        for row in result:
            print(f"{row}")

        if output_filename:
            line_str: str = ""

            with open(f"{output_filename}_{len(result)}results.csv", "w") as f:
                f.write(",".join(output_fields) + "\n")
                for row in result:
                    result_row = [str(row[field]) for field in output_fields]
                    line_str = ",".join(result_row)
                    f.write(line_str)
                    f.write("\n")


if __name__ == "__main__":
    INPUT_FILEPATH: str = (
        "../2-RDF/ontology7/pizza_restaurants_with_reasoning_sparql1.ttl"
    )

    pr_graph = PizzaRestaurantGraph(filename=INPUT_FILEPATH)

    TASK: Task = Task.SPARQL2.value
    TASK: Task = Task.SPARQL3.value
    # TASK: Task = Task.SPARQL4.value
    # TASK: Task = Task.SPARQL5.value

    if TASK == Task.SPARQL2.value:
        OUTPUT_FIELDS = [
            "restaurant",
            "name",
            "address",
            "city",
            "state",
            "postcode",
            "country",
        ]

        # QUERY: str = """
        #     SELECT ?restaurant
        #     WHERE {
        #         {
        #             ?restaurant fp:hasMenuItem ?x .
        #             ?x fp:name "pizza bianca"^^xsd:string .
        #         } UNION
        #         {
        #             ?restaurant fp:hasMenuItem ?x .
        #             ?x fp:name "white pizza"^^xsd:string .
        #         }
        #     }
        #     """

        QUERY: str = """
            SELECT DISTINCT ?restaurant ?name ?address ?city ?state ?postcode ?country
            WHERE {
                ?restaurant fp:hasMenuItem ?x .
                ?x rdf:type fp:PizzaBianca .
                ?restaurant fp:name ?name .
                ?restaurant fp:address ?address .
                ?restaurant fp:city ?city .
                ?restaurant fp:state ?state .
                OPTIONAL { ?restaurant fp:postcode ?postcode . }
                ?restaurant fp:country ?country .
            }
        """

        pr_graph.query_graph(
            query=QUERY, output_filename=TASK, output_fields=OUTPUT_FIELDS
        )

    elif TASK == Task.SPARQL3.value:

        OUTPUT_FIELDS = ["pizza", "price"]
        # OUTPUT_FIELDS = ["avg_price_margherita_pizza"]

        QUERY: str = """
            SELECT ?pizza ?name ?price
            WHERE {
                ?pizza rdf:type fp:PizzaMargherita .
                ?pizza rdf:type fp:MenuItem .
                ?pizza fp:name ?name .
                ?pizza fp:menu_item_price ?price .
            }
            """

        # QUERY: str = """
        #     SELECT (AVG(?price)) AS ?avg_price
        #     WHERE {
        #         ?pizza rdf:type fp:PizzaMargherita .
        #         ?pizza rdf:type fp:MenuItem .
        #         ?pizza fp:menu_item_price ?price .
        #     }
        #     """
        # QUERY: str = """
        #     SELECT (AVG(?price)) AS ?avg_price
        #     WHERE {
        #         ?pizza rdf:type fp:PizzaBianca .
        #         ?pizza rdf:type fp:MenuItem .
        #         ?pizza fp:menu_item_price ?price .
        #     }
        #     """

        pr_graph.query_graph(
            query=QUERY, output_filename=TASK, output_fields=OUTPUT_FIELDS
        )

    elif TASK == Task.SPARQL4.value:

        OUTPUT_FIELDS = ["restaurant", "city", "state", "num_restaurants"]

        QUERY: str = """
            SELECT DISTINCT ?restaurant ?city ?state (COUNT(?restaurant) AS ?num_restaurants
            WHERE {
                ?restaurant rdf:type fp:Restaurant .
                ?restaurant fp:city ?city .
                ?restaurant fp:state ?state .
            }
            GROUP BY ?city, ?state
            ORDER BY DESC(?state), DESC(?num_restaurants)
            """

        pr_graph.query_graph(
            query=QUERY, output_filename=TASK, output_fields=OUTPUT_FIELDS
        )

    elif TASK == Task.SPARQL5.value:

        OUTPUT_FIELDS = ["restaurant", "postcode"]

        QUERY: str = """
            SELECT ?restaurant ?postcode
            WHERE {
                ?restaurant fp:type fp:Restaurant .
                ?restaurant fp:postcode ?postcode .
                FILTER (isBlank(?postcode))
            }
            """

        pr_graph.query_graph(
            query=QUERY, output_filename=TASK, output_fields=OUTPUT_FIELDS
        )
