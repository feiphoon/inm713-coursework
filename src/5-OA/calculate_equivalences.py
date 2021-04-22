"""
Subtask OA.1
Subtask OA.2a
Subtask OA.2b
Subtask OA.3

Useful reference for the string similarity library used here:
https://rawgit.com/ztane/python-Levenshtein/master/docs/Levenshtein.html
"""
import rdflib
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import OWL

from load_ontology import load_classes

from enum import Enum
import Levenshtein as lev
from typing import NamedTuple, Any


# We define two result structures because
# the scores are measured differently.
class BestCandidatePairsLev(NamedTuple):
    target: str
    candidate: str
    dist_score: int


class BestCandidatePairsJW(NamedTuple):
    target: str
    candidate: str
    sim_score: float


class Task(Enum):
    OA1 = "oa1"
    OA2A = "oa2a"
    OA2B = "oa2b"
    OA3 = "oa3"


# class OntologyEquivalence:
#     def __init__(self, filename: str) -> None:
#         self.graph_a = Graph()
#         self.graph_a.parse(filename, format=guess_format(filename))
#         print(f"Loaded {len(self.graph_a)} triples for Graph A.")

#         self.graph_b = Graph()
#         self.graph_b.parse(filename, format=guess_format(filename))
#         print(f"Loaded {len(self.graph_b)} triples for Graph B.")

#     def debug(self) -> None:
#         pprint(vars(self))


def _find_best_candidate_matches_by_jaro_winkler(
    list_of_str_a: list, list_of_str_b: list
) -> BestCandidatePairsJW:
    """
    Performed amazingly:
    Jaro-Winkler distance: lev.jaro_winkler(str_a, str_b)

    [
        BestCandidatePairs(target="City", candidate="Country", dist_score=0.6357142857142857),
        BestCandidatePairs(target="Restaurant", candidate="Rosa", dist_score=0.7149999999999999),
        BestCandidatePairs(target="Country", candidate="Country", dist_score=1.0),
        BestCandidatePairs(target="Currency", candidate="Country", dist_score=0.7417857142857143),
        BestCandidatePairs(target="MenuItem", candidate="Medium", dist_score=0.7777777777777778),
        BestCandidatePairs(target="State", candidate="SauceTopping", dist_score=0.655),
        BestCandidatePairs(target="Bianca", candidate="PrinceCarlo", dist_score=0.6767676767676768),
        BestCandidatePairs(target="Pizza", candidate="Pizza", dist_score=1.0),
        BestCandidatePairs(target="Cheese", candidate="CheeseyPizza", dist_score=0.9333333333333333),
        BestCandidatePairs(target="FourCheese", candidate="FourCheesesTopping", dist_score=1.0),
        BestCandidatePairs(target="Margherita", candidate="Margherita", dist_score=1.0),
        BestCandidatePairs(target="Seafood", candidate="Soho", dist_score=0.6357142857142857),
        BestCandidatePairs(target="Sicilian", candidate="Siciliana", dist_score=0.9925925925925926),
    ]
    """
    candidate_pairs: list = []

    for str_a in list_of_str_a:
        sim_score: float = None
        best_candidate: str = None
        best_candidate_score: float = 0.0

        for str_b in list_of_str_b:
            sim_score = lev.jaro_winkler(str_a, str_b)
            # print(str_a, str_b, sim_score)

            # If new distance score is lower than
            # our recorded best, record the new best candidate.
            if sim_score > best_candidate_score:
                best_candidate_score = sim_score
                best_candidate = str_b

        candidate_pairs.append(
            BestCandidatePairsJW(
                target=str_a, candidate=best_candidate, sim_score=best_candidate_score
            )
        )

    return candidate_pairs


def _find_best_candidate_matches_by_lev_distance(
    list_of_str_a: list, list_of_str_b: list
) -> BestCandidatePairsLev:
    """
    Mediocre but expected outcomes:
    Absolute Levenshstein distance: lev.distance(str_a, str_b)

    [
        BestCandidatePairs(target="City", candidate="Mild", dist_score=3),
        BestCandidatePairs(target="Restaurant", candidate="Caprina", dist_score=7),
        BestCandidatePairs(target="Country", candidate="Country", dist_score=0),
        BestCandidatePairs(target="Currency", candidate="Caprina", dist_score=5),
        BestCandidatePairs(target="MenuItem", candidate="Medium", dist_score=5),
        BestCandidatePairs(target="State", candidate="Hot", dist_score=4),
        BestCandidatePairs(target="Bianca", candidate="Pizza", dist_score=4),
        BestCandidatePairs(target="Pizza", candidate="Pizza", dist_score=0),
        BestCandidatePairs(target="Cheese", candidate="Cajun", dist_score=5),
        BestCandidatePairs(target="FourCheese", candidate="FourSeasons", dist_score=6),
        BestCandidatePairs(target="Margherita", candidate="Margherita", dist_score=0),
        BestCandidatePairs(target="Seafood", candidate="Food", dist_score=4),
        BestCandidatePairs(target="Sicilian", candidate="Siciliana", dist_score=1),
    ]
    """
    candidate_pairs: list = []

    for str_a in list_of_str_a:
        sim_score: int = None
        best_candidate: str = None
        best_candidate_score: int = 10000000

        for str_b in list_of_str_b:
            sim_score = lev.distance(str_a, str_b)
            # print(str_a, str_b, sim_score)

            # If new distance score is lower than
            # our recorded best, record the new best candidate.
            if sim_score < best_candidate_score:
                best_candidate_score = sim_score
                best_candidate = str_b

        candidate_pairs.append(
            BestCandidatePairsLev(
                target=str_a, candidate=best_candidate, dist_score=best_candidate_score
            )
        )

    return candidate_pairs


def _convert_entity_to_str(ent: Any) -> str:
    return str(ent).split(".")[1]


def _createURIForEntity(entity_name: str, ns_str: str) -> str:
    return ns_str + entity_name.replace(" ", "_")


def _create_object_equivalence_triples_from_candidate_pairs(
    graph: rdflib.Graph,
    candidate_pairs: BestCandidatePairsJW,
    target_ns_str: str,
    candidate_ns_str: str,
    predicate: rdflib.term.URIRef,
) -> None:
    """
    Mappings to create equivalence triples of the form:
    fp:Margherita owl:equivalentClass pizza:Margherita
    """
    for (target, candidate, _) in candidate_pairs:
        target_uri: str = _createURIForEntity(entity_name=target, ns_str=target_ns_str)
        candidate_uri: str = _createURIForEntity(
            entity_name=candidate, ns_str=candidate_ns_str
        )

        graph.add((URIRef(target_uri), predicate, URIRef(candidate_uri)))


def _save_graph(graph: rdflib.Graph, output_file: str) -> None:
    # print(self.g.serialize(format="turtle").decode("utf-8"))
    graph.serialize(destination=output_file, format="ttl")


def run_task_oa1(filename_a: str, filename_b: str) -> None:
    # Calculate best match candidates
    klasses_a: list = load_classes(filename_a)
    klasses_b: list = load_classes(filename_b)

    klasses_a = [_convert_entity_to_str(_) for _ in klasses_a]
    klasses_b = [_convert_entity_to_str(_) for _ in klasses_b]

    results: list[BestCandidatePairsJW] = _find_best_candidate_matches_by_jaro_winkler(
        klasses_a, klasses_b
    )

    # Extract the ones which have a high enough similarity.
    # "High enough" at the moment is determined by eyeballing the results
    # and taking what we want :)
    best_candidate_pairs: list[BestCandidatePairsJW] = [
        pair for pair in results if pair.sim_score > 0.99
    ]

    # Remove Country, as the meaning is different in both ontologies
    # but correct within both their contexts.
    # We also remove FourCheese as sadly its match FourCheeseTopping
    # in the Pizza ontology has a different meaning/terminology in
    # the anatomy of a pizza.
    best_candidate_pairs = [
        pair
        for pair in best_candidate_pairs
        if (pair.target != "Country") and (pair.target != "FourCheese")
    ]

    # Now we instantiate a graph to load both ontologies for alignment
    TARGET_NAMESPACE_STR: str = "http://www.city.ac.uk/ds/inm713/feiphoon#"
    TARGET_NAMESPACE: rdflib.Namespace = Namespace(TARGET_NAMESPACE_STR)
    TARGET_PREFIX: str = "fp"

    CANDIDATE_NAMESPACE_STR: str = "http://www.co-ode.org/ontologies/pizza/pizza.owl#"
    CANDIDATE_NAMESPACE: rdflib.Namespace = Namespace(CANDIDATE_NAMESPACE_STR)
    CANDIDATE_PREFIX: str = "pizza"

    OWL_NAMESPACE: rdflib.Namespace = Namespace("http://www.w3.org/2002/07/owl#")
    OWL_PREFIX: str = "owl"

    graph: rdflib.Graph = Graph()
    graph.bind(prefix=TARGET_PREFIX, namespace=TARGET_NAMESPACE)
    graph.bind(prefix=CANDIDATE_PREFIX, namespace=CANDIDATE_NAMESPACE)
    graph.bind(prefix=OWL_PREFIX, namespace=OWL_NAMESPACE)

    # The pizza ontology has no data properties, and a few object
    # properties that won't match what we have currently, so we'll
    # only produce equivalent classes, and only for things we want
    # to align.
    _create_object_equivalence_triples_from_candidate_pairs(
        graph=graph,
        candidate_pairs=best_candidate_pairs,
        target_ns_str=TARGET_NAMESPACE_STR,
        candidate_ns_str=CANDIDATE_NAMESPACE_STR,
        predicate=OWL.equivalentClass,
    )

    _save_graph(graph=graph, output_file=f"equivalence_triples_{Task.OA1.value}.ttl")


if __name__ == "__main__":
    INPUT_FILEPATH_A: str = "../1-OWL/pizza_restaurant_ontology8.owl"
    INPUT_FILEPATH_B: str = "../data/pizza_manchester.owl"

    TASK: Task = Task.OA1.value
    # TASK: Task = Task.OA2A.value
    # TASK: Task = Task.OA2B.value
    # TASK: Task = Task.OA3.value

    if TASK == Task.OA1.value:
        run_task_oa1(filename_a=INPUT_FILEPATH_A, filename_b=INPUT_FILEPATH_B)

    elif TASK == Task.OA2A.value:
        pass
    elif TASK == Task.OA2B.value:
        pass
    elif TASK == Task.OA3.value:
        pass
