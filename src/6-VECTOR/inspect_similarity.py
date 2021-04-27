"""
Modified from code from INM713 labs/gensim KeyedVector examples:

https://github.com/RaRe-Technologies/gensim/blob/2feef89a24c222e4e0fc6e32ac7c6added752c26/gensim/models/keyedvectors.py
https://radimrehurek.com/gensim/models/keyedvectors.html

Subtask VECTOR.1
Subtask VECTOR.2

Embeddings created from the file:
/src/6-VECTOR/Standalone_01/pizza_restaurants_with_reasoning_sparql1.rdf
"""
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
    model = KeyedVectors.load(embeddings_filename, mmap="r")
    # vector = wv[str1]  # Get numpy vector of a word
    # print(vector)

    # for key in model.wv.vocab:
    #     print(key)
    sim_score = model.wv.similarity(str1, str2)
    # 1.0 if perfect match
    print(f"{str1}, {str2}: {sim_score}")
    return PairSimilarity(str1=str1, str2=str2, sim_score=sim_score)


def get_most_similar(
    embeddings_filename: str, positive_list: list, negative_list: list = None
) -> EmbeddingSimilarity:
    model = KeyedVectors.load(embeddings_filename, mmap="r")
    result = model.wv.most_similar(positive=positive_list, negative=negative_list)
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
    model = KeyedVectors.load(embeddings_filename, mmap="r")
    result = model.wv.most_similar_cosmul(
        positive=positive_list, negative=negative_list
    )
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


if __name__ == "__main__":
    # String pair similarity
    # get_pair_similarity(
    #     embeddings_filename="Standalone_01/output_embedding/config3.embeddings",
    #     str1="pizza",
    #     str2="pizza",
    # )

    # How are fp:Pizza and pizza related?
    # http://www.city.ac.uk/ds/inm713/feiphoon#Pizza, pizza: 0.44109153747558594
    # get_pair_similarity(
    #     embeddings_filename="Standalone_01/output_embedding/config3.embeddings",
    #     str1="http://www.city.ac.uk/ds/inm713/feiphoon#Pizza",
    #     str2="pizza",
    # )

    # How closely related are fp:MenuItem and fp:Restaurant?
    # http://www.city.ac.uk/ds/inm713/feiphoon#MenuItem, http://www.city.ac.uk/ds/inm713/feiphoon#Restaurant: 0.49134278297424316
    # get_pair_similarity(
    #     embeddings_filename="Standalone_01/output_embedding/config3.embeddings",
    #     str1="http://www.city.ac.uk/ds/inm713/feiphoon#MenuItem",
    #     str2="http://www.city.ac.uk/ds/inm713/feiphoon#Restaurant",
    # )

    # Can we associate margherita pizza with margarita pizza?
    # margherita pizza, margarita pizza: 0.5124445557594299
    # get_pair_similarity(
    #     embeddings_filename="Standalone_01/output_embedding/config3.embeddings",
    #     str1="margherita pizza",
    #     str2="margarita pizza",
    # )

    # http://www.city.ac.uk/ds/inm713/feiphoon#Margherita: 0.8818
    # The rest of the results:
    # [('http://www.city.ac.uk/ds/inm713/feiphoon#Margherita', 0.8817708492279053),
    # ('pizza margherita', 0.8427455425262451),
    # ('margherita pizza', 0.8416988849639893),
    # ('are', 0.8386538624763489),
    # ('items', 0.8299614787101746),
    # ('bianca', 0.8247273564338684),
    # ('seafood', 0.8070252537727356),
    # ('sicilian', 0.7978703379631042),
    # ('menu', 0.7959816455841064),
    # ('type', 0.7936738729476929)]
    # get_most_similar_cosmul(
    #     embeddings_filename="Standalone_01/output_embedding/config3.embeddings",
    #     positive_list=["margherita"],
    # )

    # new york: 0.8997
    # The rest of the results:
    # [('new york', 0.8996528387069702),
    # ('new york city', 0.8980041742324829),
    # ('new city', 0.8964184522628784),
    # ('New York', 0.8895120620727539),
    # ('New York City', 0.886168360710144),
    # ('New City', 0.8828853368759155),
    # ('http://dbpedia.org/resource/Manhattan', 0.8825619220733643),
    # ('York', 0.880652666091919),
    # ('http://www.city.ac.uk/ds/inm713/feiphoon#rosa_mexicano_1063_1st_ave_new_york_manhattan_10022_us', 0.852108359336853),
    # ('http://www.city.ac.uk/ds/inm713/feiphoon#coral_restaurant_3801_broadway_new_york_nyc_10032_us', 0.839216411113739)]
    # get_most_similar_cosmul(
    #     embeddings_filename="Standalone_01/output_embedding/config3.embeddings",
    #     positive_list=["http://dbpedia.org/resource/New_York_City"],
    # )

    # http://www.city.ac.uk/ds/inm713/feiphoon#burgers_and_cupcakes_458_9th_ave_new_york_nyc_10018_us: 1.4381
    # The rest of the results:
    # [('http://www.city.ac.uk/ds/inm713/feiphoon#burgers_and_cupcakes_458_9th_ave_new_york_nyc_10018_us', 1.4380625486373901),
    # ('http://www.city.ac.uk/ds/inm713/feiphoon#lil_frankies_19_first_ave_new_york_manhattan_10003_us', 1.4312268495559692),
    # ('http://www.city.ac.uk/ds/inm713/feiphoon#gran_morsi_22_warren_st_new_york_manhattan_10007_us', 1.4271714687347412),
    # ('http://www.city.ac.uk/ds/inm713/feiphoon#caseys_general_store_1822_n_lincoln_ave_york_ne_68467_us', 1.4235228300094604),
    # ('http://www.city.ac.uk/ds/inm713/feiphoon#bodrum_turkish_mediterranean_584_amsterdam_ave_new_york_nyc_10024_us', 1.4231888055801392),
    # ('http://www.city.ac.uk/ds/inm713/feiphoon#little_italy_pizza_deli_180_varick_st_new_york_nyc_10014_us', 1.420847773551941),
    # ('York', 1.4157843589782715),
    # ('http://www.city.ac.uk/ds/inm713/feiphoon#tavola_488_9th_ave_new_york_nyc_10018_us', 1.412175178527832),
    # ('http://www.city.ac.uk/ds/inm713/feiphoon#cinema_cafe_restaurant_505_3rd_ave_new_york_nyc_10016_us', 1.4050695896148682),
    # ('http://www.city.ac.uk/ds/inm713/feiphoon#gran_morsi_22_warren_st_new_york_manhattan_10007_us_bronx_bomber_pizza', 1.3964817523956299)]
    # get_most_similar_cosmul(
    #     embeddings_filename="Standalone_01/output_embedding/config3.embeddings",
    #     positive_list=["http://dbpedia.org/resource/New_York_City"],
    #     negative_list=["city"],
    # )

    # What kind of crust is common?
    # thin: 0.9219
    # The rest of the results:
    # [('thin', 0.9218510985374451),
    # ('spaghetti', 0.8372948169708252),
    # ('thin crust pizza', 0.8314130306243896),
    # ('bellablanca thin crust pizza', 0.8229946494102478),
    # ('hawiian thin crust pizza', 0.8205676674842834),
    # ('mediterranean thin crust pizza', 0.8196155428886414),
    # ('cheese thin crust pizza', 0.8179678320884705),
    # ('fare soldi thin crust pizza', 0.8178261518478394),
    # ('bacon cheeseburger thin crust pizza', 0.8147181868553162),
    # ('with beef, chicken, meatballs, sausage, bacon, pepperoni and ham.', 0.8136087656021118)]
    # get_most_similar_cosmul(
    #     embeddings_filename="Standalone_01/output_embedding/config3.embeddings",
    #     positive_list=["crust"],
    # )

    # hawaiian pizza: 0.9087
    # The rest of the results:
    # [('hawaiian pizza', 0.9086912274360657),
    # ('home made pizza, prosciutto di parma, guanciale four cheese sauce, waimanalo baby arugula', 0.7783111333847046),
    # ('meat', 0.7673579454421997),
    # ('pizza prosciutto con arugula', 0.7643983364105225),
    # ('rainbow bazaar hilton hawaiian vlg', 0.7637658715248108),
    # ('18.96', 0.762822151184082), ('pizza prosciutto con arugula combination', 0.7600585222244263),
    # ('bacon', 0.7579233646392822),
    # ('rainbow', 0.7575806379318237),
    # ('16.97', 0.7548248767852783)]
    # get_most_similar_cosmul(
    #     embeddings_filename="Standalone_01/output_embedding/config3.embeddings",
    #     positive_list=["hawaiian"],
    # )

    # honolulu: 1.5123
    # The rest of the results:
    # [('honolulu', 1.5123459100723267),
    # ('combination', 1.4701669216156006),
    # ('hawaiian pizza', 1.4658058881759644),
    # ('http://www.city.ac.uk/ds/inm713/feiphoon#fresco_rainbow_bazaar_hilton_hawaiian_vlg_honolulu_hono_96815_us', 1.4577504396438599),
    # ('hono', 1.4519562721252441),
    # ('honor', 1.435217022895813),
    # ('96815', 1.4331459999084473),
    # ('rainbow', 1.4244738817214966),
    # ('rainbow bazaar hilton hawaiian vlg', 1.4216058254241943),
    # ('fresco', 1.4078315496444702)]
    # get_most_similar_cosmul(
    #     embeddings_filename="Standalone_01/output_embedding/config3.embeddings",
    #     positive_list=["hawaiian"],
    #     negative_list=["1.0"],
    # )

    # What is pizza? Unfortunately there's a lot of stop words in the results.
    # us: 0.9146
    # The rest of the results:
    # [('us', 0.9145568013191223),
    # ('items', 0.8713830709457397),
    # ('are', 0.8712526559829712),
    # ('type', 0.869111180305481),
    # ('of', 0.8564725518226624),
    # ('that', 0.833275556564331),
    # ('sicilian', 0.8287044167518616),
    # ('by', 0.8265051245689392),
    # ("roula's", 0.8247994780540466),
    # ('bianca', 0.8232169151306152)]
    # get_most_similar_cosmul(
    #     embeddings_filename="Standalone_01/output_embedding/config3.embeddings",
    #     positive_list=["pizza"],
    # )

    # nonna's pizza: 0.9851
    # The rest of the results:
    # [("nonna's pizza", 0.9851227402687073),
    # ('52 lake st', 0.9741149544715881),
    # ('crushed tomato garlic fresh basil olive oil parmesan cheese', 0.9659836888313293),
    # ('ricotta mozzarella and sauce', 0.960893452167511),
    # ('ham pineapple and bacon', 0.9542688727378845),
    # ('mozzarella ricotta chopped meat', 0.9469665884971619),
    # ('marinara square pizza', 0.9461687207221985),
    # ('pepperoni, ham sausage and bacon', 0.9459295868873596),
    # ('sliced tomato fresh mozzarella basil olive oil', 0.945704996585846),
    # ('bbq or buffalo chicken', 0.9452654123306274)]
    # get_most_similar_cosmul(
    #     embeddings_filename="Standalone_01/output_embedding/config3.embeddings",
    #     positive_list=["nonna's"],
    # )

    # Config1 seems better for longer string/phrase searches.
    # We can find the shop with branches that has the signature pizza
    # This found 4 of the 5 locations this shop has.
    # california pizza kitchen: 0.3852
    # The rest of the results:
    # [('california pizza kitchen', 0.38517358899116516),
    # ('zo��s', 0.36109331250190735),
    # ('http://www.city.ac.uk/ds/inm713/feiphoon#california_pizza_kitchen_109_w_county_ctr_saint_louis_country_life_acres_63131_us_the_original_bbq_chicken_pizza', 0.3532891869544983),
    # ('http://www.city.ac.uk/ds/inm713/feiphoon#california_pizza_kitchen_3401_esperanza_xing_austin_tx_78758_us_the_original_bbq_chicken_pizza', 0.35289883613586426),
    # ('http://www.city.ac.uk/ds/inm713/feiphoon#california_pizza_kitchen_10300_forest_hill_blvd_wellington_village_of_wellington_33414_us_the_original_bbq_chicken_pizza', 0.3517822325229645),
    # ("austin's", 0.3516727089881897),
    # ('morrisania', 0.3471701145172119),
    # ('devils', 0.34549203515052795),
    # ('http://www.city.ac.uk/ds/inm713/feiphoon#california_pizza_kitchen_11800_w_broad_st_henrico_va_23233_us_the_original_bbq_chicken_pizza', 0.3442400395870209),
    # ('created here in 1985. our legendary bbq sauce, smoked gouda, red onions and fresh cilantro transform this original to iconic', 0.34276875853538513)]
    # get_most_similar_cosmul(
    #     embeddings_filename="Standalone_01/output_embedding/config1.embeddings",
    #     positive_list=["california", "pizza", "original"],
    # )

    # What is a sushi pizza?
    # spicy tuna, mango, avocado, crunchy, scallion tobiko, eel sauce, mango: 0.5124
    # The rest of the results:
    # [('spicy tuna, mango, avocado, crunchy, scallion tobiko, eel sauce, mango', 0.5124293565750122),
    # ('popped rice topped with assorted raw fish, tobiko, avocado, scallion, onion, shrimp paste and spicy mayonaise', 0.5106814503669739),
    # ('crunchy batter mixed w. krab meat, roe, and green onion on top of deep fried rice', 0.509605884552002),
    # ('tuna salmon seaweed salad onion with sauce on scallion pancake', 0.5090429186820984),
    # ('toyo japanese sushi bar & hibachi', 0.5082502961158752),
    # ('nana sushi', 0.5079037547111511),
    # ('spicy tuna. mango, avocado, crunchy, scallion tobiko, eel sauce, mango .', 0.5029162168502808),
    # ('fried pizza dough topped with spicy tuna, avocado, scallion tobiko crunch', 0.5012624859809875),
    # ('ya ya noodles chinese restaurant', 0.5007303357124329),
    # ('tomo steak and sushi', 0.5002437233924866)]
    # get_most_similar_cosmul(
    #     embeddings_filename="Standalone_01/output_embedding/config1.embeddings",
    #     positive_list=["sushi", "pizza"],
    # )

    # bianca: 0.7648
    # The rest of the results:
    # [('bianca', 0.7648218870162964),
    # ('http://www.city.ac.uk/ds/inm713/feiphoon#FourCheese', 0.7503757476806641),
    # ('(two toppings each), 60 wings and four 2 liters of soda.', 0.7476459741592407),
    # ('items', 0.7468879222869873),
    # ('seafood', 0.7450354099273682),
    # ('liguria italian pepperoni, roma pear tomato sauce and four cheese blend', 0.7438399791717529),
    # ('http://www.city.ac.uk/ds/inm713/feiphoon#Cheese', 0.7418898344039917), \
    # ('margherita', 0.7389877438545227),
    # ('http://www.city.ac.uk/ds/inm713/feiphoon#Seafood', 0.7389434576034546),
    # ('http://www.city.ac.uk/ds/inm713/feiphoon#Sicilian', 0.7375236749649048)]
    # get_most_similar_cosmul(
    #     embeddings_filename="Standalone_01/output_embedding/config1.embeddings",
    #     positive_list=["cheese"],
    # )

    # Mozzarella.: 0.5394
    # The rest of the results:
    # [('Mozzarella.', 0.5393903851509094),
    # ('Fontinella.', 0.5349646806716919),
    # ('always a favorite', 0.5281090140342712),
    # ('broccoli, tomatoes, garlic and mozzarella cheese', 0.5251507759094238),
    # ('fresh garlic, broccoli, shrimp, pepper, olive oil, parmesan cheese', 0.5250117182731628),
    # ('ricotta, garlic, and mozzarella.', 0.5196033716201782),
    # ('bacon, tomatoes, garlic and mozzarella cheese', 0.5195278525352478),
    # ("delosa's", 0.5191994905471802),
    # ('large.', 0.5168597102165222),
    # ('truffle infused spicy sausage, mozzarella, grana padano, basil, evoo', 0.5145997405052185)]
    get_most_similar_cosmul(
        embeddings_filename="Standalone_01/output_embedding/config1.embeddings",
        positive_list=["tomato", "pizza"],
    )
