"""
Subtask OA.1
Subtask OA.2a
Subtask OA.2b
Subtask OA.3
"""
from rdflib import Graph
from rdflib.util import guess_format

from enum import Enum
from pprint import pprint


class Task(Enum):
    OA1 = "oa1"
    OA2A = "oa2a"
    OA2B = "oa2b"
    OA3 = "oa3"


class OntologyEquivalence:
    def __init__(self, filename: str) -> None:
        self.graph_a = Graph()
        self.graph_a.parse(filename, format=guess_format(filename))
        print(f"Loaded {len(self.graph_a)} triples for Graph A.")

        self.graph_b = Graph()
        self.graph_b.parse(filename, format=guess_format(filename))
        print(f"Loaded {len(self.graph_b)} triples for Graph B.")

    def debug(self) -> None:
        pprint(vars(self))

    # def display(self) -> None:
    #     for s, p, o in self.graph:
    #         print((s.n3(), p.n3(), o.n3()))
    #     print(f"Printed {len(self.graph)} triples.")

    # def query_graph(
    #     self, query: str, output_filename: str = "", output_fields: list = []
    # ) -> None:
    #     result = self.graph.query(query)

    #     print(f"Found {len(result)} results.")
    #     for row in result:
    #         print(f"{row}")

    #     if output_filename:
    #         line_str: str = ""

    #         with open(f"{output_filename}_{len(result)}results.csv", "w") as f:
    #             f.write(",".join(output_fields) + "\n")
    #             for row in result:
    #                 result_row = [str(row[field]) for field in output_fields]
    #                 line_str = ",".join(result_row)
    #                 f.write(line_str)
    #                 f.write("\n")


if __name__ == "__main__":
    INPUT_FILEPATH: str = (
        "../2-RDF/ontology7/pizza_restaurants_with_reasoning_sparql1.ttl"
    )

    oe = OntologyEquivalence(filename=INPUT_FILEPATH)