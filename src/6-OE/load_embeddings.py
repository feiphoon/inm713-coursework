"""
Modified from code from INM713 labs.

https://radimrehurek.com/gensim/models/keyedvectors.html

Subtask VECTOR.1
Subtask VECTOR.2
"""
# Load back with memory-mapping = read-only, shared across processes.
from gensim.models import KeyedVectors
from typing import NamedTuple, List


class PairSimilarity(NamedTuple):
    str1: str
    str2: str
    sim_score: float


class EmbeddingSimilarity(NamedTuple):
    positive_list: list
    negative_list: list
    best_match: str
    best_sim_score: float
    result: List[tuple]


def get_pair_similarity(
    embeddings_filename: str, str1: str, str2: str
) -> PairSimilarity:
    wv = KeyedVectors.load(embeddings_filename, mmap="r")
    # vector = wv[str1]  # Get numpy vector of a word
    # print(vector)

    # for key in wv.wv.vocab:
    #     print(key)

    sim_score = wv.wv.similarity(str1, str2)
    # 1.0 if perfect match
    print(f"{str1}, {str2}: {sim_score}")
    return PairSimilarity(str1=str1, str2=str2, sim_score=sim_score)


def get_most_similar(
    embeddings_filename: str, positive_list: list, negative_list: list = None
) -> EmbeddingSimilarity:
    wv = KeyedVectors.load(embeddings_filename, mmap="r")
    result = wv.wv.most_similar(positive=positive_list, negative=negative_list)
    most_similar_key, best_sim_score = result[0]

    print(f"{most_similar_key}: {best_sim_score:.4f}")
    print(f"The rest of the results: {result}")

    return EmbeddingSimilarity(
        positive_list=positive_list,
        negative_list=negative_list,
        best_match=most_similar_key,
        best_sim_score=best_sim_score,
        result=result,
    )


def get_most_similar_cosmul(
    embeddings_filename: str, positive_list: list, negative_list: list = None
) -> EmbeddingSimilarity:
    wv = KeyedVectors.load(embeddings_filename, mmap="r")

    result = wv.wv.most_similar_cosmul(positive=positive_list, negative=negative_list)
    most_similar_key, best_sim_score = result[0]

    print(f"{most_similar_key}: {best_sim_score:.4f}")
    print(f"The rest of the results: {result}")

    return EmbeddingSimilarity(
        positive_list=positive_list,
        negative_list=negative_list,
        best_match=most_similar_key,
        best_sim_score=best_sim_score,
        result=result,
    )


# String pair similarity
get_pair_similarity(
    embeddings_filename="Standalone_01/output_embedding/config3.embeddings",
    str1="pizza",
    str2="pizza",
)

get_pair_similarity(
    embeddings_filename="Standalone_01/output_embedding/config3.embeddings",
    str1="http://www.city.ac.uk/ds/inm713/feiphoon#Pizza",
    str2="pizza",
)

get_pair_similarity(
    embeddings_filename="Standalone_01/output_embedding/config3.embeddings",
    str1="http://www.city.ac.uk/ds/inm713/feiphoon#isMenuItemAt",
    str2="http://www.city.ac.uk/ds/inm713/feiphoon#Pizza",
)

get_pair_similarity(
    embeddings_filename="Standalone_01/output_embedding/config3.embeddings",
    str1="margherita",
    str2="margarita",
)

get_pair_similarity(
    embeddings_filename="Standalone_01/output_embedding/config3.embeddings",
    str1="margherita",
    str2="margarita",
)

get_pair_similarity(
    embeddings_filename="Standalone_01/output_embedding/config3.embeddings",
    str1="http://dbpedia.org/resource/New_York_City",
    str2="pizza",
)

get_most_similar(
    embeddings_filename="Standalone_01/output_embedding/config3.embeddings",
    positive_list=["New", "York", "pizza"],
)

get_most_similar_cosmul(
    embeddings_filename="Standalone_01/output_embedding/config3.embeddings",
    positive_list=["New", "York", "pizza"],
)

# Config1 seems better for longer string searches.
# We can find the shop with branches that has the signature pizza
get_most_similar(
    embeddings_filename="Standalone_01/output_embedding/config1.embeddings",
    positive_list=["california", "pizza", "original"],
)

get_most_similar(
    embeddings_filename="Standalone_01/output_embedding/config1.embeddings",
    positive_list=["sushi", "pizza"],
)

get_most_similar(
    embeddings_filename="Standalone_01/output_embedding/config1.embeddings",
    positive_list=["seafood", "pizza"],
)
