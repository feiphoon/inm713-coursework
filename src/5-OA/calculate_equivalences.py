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
from rdflib.util import guess_format
import owlrl
from owlready2 import *  # noqa F403

from load_ontology import load_classes, load_object_properties

import time
import re
from enum import Enum
import Levenshtein as lev
from typing import NamedTuple, Any
from googletrans import Translator


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


class BestCandidatePairsJWTranslated(NamedTuple):
    target: str
    candidate: str
    translated_candidate: str
    sim_score: float


class Task(Enum):
    OA1 = "oa1"
    OA2 = "oa2"


def _find_best_candidate_matches_by_jaro_winkler(
    target_list: list, candidate_list: list
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

    for target in target_list:
        sim_score: float = None
        best_candidate: str = None
        best_candidate_score: float = 0.0

        for candidate in candidate_list:
            sim_score = lev.jaro_winkler(target, candidate)

            # If new distance score is lower than
            # our recorded best, record the new best candidate.
            if sim_score > best_candidate_score:
                best_candidate_score = sim_score
                best_candidate = candidate

        candidate_pairs.append(
            BestCandidatePairsJW(
                target=target, candidate=best_candidate, sim_score=best_candidate_score
            )
        )

    return candidate_pairs


def _find_best_candidate_matches_by_jaro_winkler_with_translation(
    target_list: list, candidate_list: list, target_lang: str = "en"
) -> BestCandidatePairsJWTranslated:
    """
    Using googletrans library.
    Jaro-Winkler distance: lev.jaro_winkler(str_a, str_b)
    """
    translator = Translator(
        service_urls=[
            "translate.google.com",
            "translate.google.co.uk",
        ]
    )
    candidate_pairs: list = []

    for target in target_list:
        print("hey")
        sim_score: float = None
        best_candidate: str = None
        translated_best_candidate: str = None
        best_candidate_score: float = 0.0

        for candidate in candidate_list:
            preprocessed_candidate = " ".join(
                re.sub(r"([A-Z])", r" \1", candidate).split()
            ).lower()
            print(preprocessed_candidate)
            translated_candidate = translator.translate(
                preprocessed_candidate, to_lang=target_lang
            ).text
            sim_score = lev.jaro_winkler(target, translated_candidate)

            # If new distance score is lower than
            # our recorded best, record the new best candidate.
            if sim_score > best_candidate_score:
                best_candidate_score = sim_score
                best_candidate = candidate
                translated_best_candidate = translated_candidate

        candidate_pairs.append(
            BestCandidatePairsJWTranslated(
                target=target,
                candidate=best_candidate,
                translated_candidate=translated_best_candidate,
                sim_score=best_candidate_score,
            )
        )

    return candidate_pairs


def _find_best_candidate_matches_by_lev_distance(
    target_list: list, candidate_list: list
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

    for target in target_list:
        sim_score: int = None
        best_candidate: str = None
        best_candidate_score: int = 10000000

        for candidate in candidate_list:
            sim_score = lev.distance(target, candidate)

            # If new distance score is lower than
            # our recorded best, record the new best candidate.
            if sim_score < best_candidate_score:
                best_candidate_score = sim_score
                best_candidate = candidate

        candidate_pairs.append(
            BestCandidatePairsLev(
                target=target, candidate=best_candidate, dist_score=best_candidate_score
            )
        )

    return candidate_pairs


def _convert_entity_to_str(ent: Any) -> str:
    return str(ent).split(".")[1]


def _createURIForEntity(entity_name: str, ns_str: str) -> str:
    return ns_str + entity_name.replace(" ", "_")


def _create_equivalence_triples_from_candidate_pairs(
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
    for target, candidate, *_ in candidate_pairs:
        target_uri: str = _createURIForEntity(entity_name=target, ns_str=target_ns_str)
        candidate_uri: str = _createURIForEntity(
            entity_name=candidate, ns_str=candidate_ns_str
        )

        graph.add((URIRef(target_uri), predicate, URIRef(candidate_uri)))


# def perform_reasoning(ontology_file: str) -> None:
#     """
#     Subtask OA.2
#     Expand the graph with the inferred triples, using reasoning.
#     """
#     tic = time.perf_counter()
#     # print(guess_format(ontology_file))
#     self.graph.load(ontology_file, format=guess_format(ontology_file))

#     print(f"Triples including ontology: {len(self.graph)}.")

#     # Happy with this reasoner
#     owlrl.DeductiveClosure(
#         owlrl.OWLRL.OWLRL_Semantics,
#         axiomatic_triples=False,
#         datatype_axioms=False,
#     ).expand(self.graph)

#     toc = time.perf_counter()
#     print(f"Finished reasoning on graph in {toc - tic} seconds.")
#     print(f"Triples after OWL 2 RL reasoning: {len(self.graph)}.")


def _save_graph(graph: rdflib.Graph, output_file: str) -> None:
    # print(self.g.serialize(format="turtle").decode("utf-8"))
    graph.serialize(destination=output_file, format="ttl")


def run_task_oa1(
    filename_a: str, filename_b: str, with_translation: bool = False
) -> None:
    # Load classes from both ontologies for matching
    klasses_a: list = load_classes(filename_a)
    klasses_b: list = load_classes(filename_b)

    klasses_a = [_convert_entity_to_str(_) for _ in klasses_a]
    klasses_b = [_convert_entity_to_str(_) for _ in klasses_b]

    # Load object properties from both ontologies for matching
    obj_properties_a: list = load_object_properties(filename_a)
    obj_properties_b: list = load_object_properties(filename_b)

    obj_properties_a = [_convert_entity_to_str(_) for _ in obj_properties_a]
    obj_properties_b = [_convert_entity_to_str(_) for _ in obj_properties_b]

    if not with_translation:
        # Jaro Winkler matching without translation
        results: list[
            BestCandidatePairsJW
        ] = _find_best_candidate_matches_by_jaro_winkler(
            target_list=klasses_a, candidate_list=klasses_b
        )

        # Get best match candidates and extract the ones which
        # have a high enough similarity.
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

        # # This is for object properties, but we won't apply them.
        # results_obj_property: list[
        #     BestCandidatePairsJW
        # ] = _find_best_candidate_matches_by_jaro_winkler(
        #     target_list=obj_properties_a, candidate_list=obj_properties_b
        # )
        # best_obj_property_candidate_pairs: list[BestCandidatePairsJW] = [
        #     pair for pair in results_obj_property if pair.sim_score > 0.99
        # ]

    else:
        # Just for exploration, Jaro Winkler matching with translation.
        # WARNING: this is extremely flaky, because:
        # - googletrans is not an official library
        # - googletrans uses the Google Translate API and it
        # does not give the same results as the web service.
        # - I think there is rate limiting, which causes
        # requests to fail silently as no translation performed.
        # The alternative is to batch requests, but we won't go
        # there this time.
        # If you'd like to try this, use example lists of:
        # ["FourCheeses"], ["QuattroFormaggi"].
        results: list[
            BestCandidatePairsJWTranslated
        ] = _find_best_candidate_matches_by_jaro_winkler_with_translation(
            target_list=klasses_a, candidate_list=klasses_b, target_lang="en"
        )
        best_candidate_pairs: list[BestCandidatePairsJWTranslated] = [
            pair for pair in results if pair.sim_score > 0.99
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
    _create_equivalence_triples_from_candidate_pairs(
        graph=graph,
        candidate_pairs=best_candidate_pairs,
        target_ns_str=TARGET_NAMESPACE_STR,
        candidate_ns_str=CANDIDATE_NAMESPACE_STR,
        predicate=OWL.equivalentClass,
    )

    # We won't use these - perhaps further improvements
    # to the upstream ontology.
    # _create_equivalence_triples_from_candidate_pairs(
    #     graph=graph,
    #     candidate_pairs=best_obj_property_candidate_pairs,
    #     target_ns_str=TARGET_NAMESPACE_STR,
    #     candidate_ns_str=CANDIDATE_NAMESPACE_STR,
    #     predicate=OWL.equivalentProperty,
    # )

    _save_graph(graph=graph, output_file=f"equivalence_triples_{Task.OA1.value}.ttl")


def run_task_oa2() -> None:

    pizza = get_ontology("ontologies/pizza_manchester.owl").load()
    pizza_restaurant = get_ontology("ontologies/pizza_restaurant_ontology8.owl").load()

    pizza.imported_ontologies.append(pizza_restaurant)
    print(pizza)

    # onto.imported_ontologies.append("pizza_restaurant_ontology8.owl")
    # onto.load()


if __name__ == "__main__":
    INPUT_FILEPATH_A: str = "../2-OWL/pizza_restaurant_ontology8.owl"
    INPUT_FILEPATH_B: str = "../data/pizza_manchester.owl"

    TASK: Task = Task.OA1.value
    TASK: Task = Task.OA2.value

    if TASK == Task.OA1.value:
        run_task_oa1(
            filename_a=INPUT_FILEPATH_A,
            filename_b=INPUT_FILEPATH_B,
            with_translation=False,
        )

    elif TASK == Task.OA2.value:
        ONTO_PATH: str = "ontologies"
        run_task_oa2()
