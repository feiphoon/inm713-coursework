# File tree

This is the file tree up to a certain depth.

The most important files for marking are listed here. Any discrepancies will only be due to more experiment results being logged or processed.

All code to be marked is found in the main folder `src`, under their respective labels according to the coursework guidelines, e.g. `src/2-OWL/` relates to Task 2.2 OWL. Each folder contains a README, any results that needed to be produced for submission, and code needed to produce them.

```
.
├── LICENSE
├── README.md
├── TREE.md
├── requirements.txt
├── src
│   ├── 1-exploration
│   │   ├── README.md
│   │   ├── exploratory_analysis.ipynb
│   │   ├── preprocessing-spike.ipynb
│   │   └── preprocessing.ipynb
│   ├── 2-OWL
│   │   ├── README.md
│   │   ├── pizza_restaurant_ontology-slim.owl
│   │   ├── pizza_restaurant_ontology.owl
│   │   ├── pizza_restaurant_ontology2.owl
│   │   ├── pizza_restaurant_ontology3-slim.owl
│   │   ├── pizza_restaurant_ontology3.owl
│   │   ├── pizza_restaurant_ontology3.ttl
│   │   ├── pizza_restaurant_ontology4-slim.owl
│   │   ├── pizza_restaurant_ontology4-slim.ttl
│   │   ├── pizza_restaurant_ontology5-owl.owl
│   │   ├── pizza_restaurant_ontology5-rdf.owl
│   │   ├── pizza_restaurant_ontology5-slim.owl
│   │   ├── pizza_restaurant_ontology5-slim.ttl
│   │   ├── pizza_restaurant_ontology5.owl
│   │   ├── pizza_restaurant_ontology5.ttl
│   │   ├── pizza_restaurant_ontology6.owl
│   │   ├── pizza_restaurant_ontology6.ttl
│   │   ├── pizza_restaurant_ontology7.owl
│   │   ├── pizza_restaurant_ontology7.ttl
│   │   ├── pizza_restaurant_ontology8.owl
│   │   ├── pizza_restaurant_ontology8.ttl
│   │   ├── pizza_restaurant_ontology9.owl
│   │   └── pizza_restaurant_ontology9.ttl
│   ├── 3-RDF
│   │   ├── ontology5
│   │   │   ├── create_rdf_triples.py
│   │   │   ├── pizza_restaurants_with_reasoning.ttl
│   │   │   └── pizza_restaurants_without_reasoning.ttl
│   │   ├── ontology6
│   │   │   ├── create_rdf_triples.py
│   │   │   ├── encode.py
│   │   │   ├── entity.py
│   │   │   ├── last_run.txt
│   │   │   ├── lookup.py
│   │   │   ├── mymath.py
│   │   │   ├── pizza_restaurants_with_reasoning_sparql1.ttl
│   │   │   ├── pizza_restaurants_without_reasoning_rdf2.ttl
│   │   │   ├── pizza_restaurants_without_reasoning_rdf3.ttl
│   │   │   └── stringcmp.py
│   │   ├── ontology7
│   │   │   ├── create_rdf_triples.py
│   │   │   ├── encode.py
│   │   │   ├── entity.py
│   │   │   ├── last_best_results
│   │   │   │   └── pizza_restaurants_with_reasoning_sparql1.ttl
│   │   │   ├── last_better_results
│   │   │   │   ├── pizza_restaurants_without_reasoning_rdf2.ttl
│   │   │   │   └── pizza_restaurants_without_reasoning_rdf3.ttl
│   │   │   ├── last_good_results
│   │   │   │   ├── pizza_restaurants_with_reasoning_sparql1.ttl
│   │   │   │   ├── pizza_restaurants_without_reasoning_rdf2.ttl
│   │   │   │   └── pizza_restaurants_without_reasoning_rdf3.ttl
│   │   │   ├── last_run.txt
│   │   │   ├── lookup.py
│   │   │   ├── mymath.py
│   │   │   ├── pizza_restaurants_with_reasoning_sparql1.ttl
│   │   │   ├── pizza_restaurants_without_reasoning_rdf2.ttl
│   │   │   ├── pizza_restaurants_without_reasoning_rdf3.ttl
│   │   │   └── stringcmp.py
│   │   ├── ontology8
│   │   │   ├── create_rdf_triples.py
│   │   │   ├── encode.py
│   │   │   ├── entity.py
│   │   │   ├── last_run.txt
│   │   │   ├── lookup.py
│   │   │   ├── mymath.py
│   │   │   ├── pizza_restaurants_with_reasoning_sparql1.rdf
│   │   │   ├── pizza_restaurants_with_reasoning_sparql1.ttl
│   │   │   ├── pizza_restaurants_without_reasoning_rdf2.ttl
│   │   │   ├── pizza_restaurants_without_reasoning_rdf3.ttl
│   │   │   └── stringcmp.py
│   │   └── testing.ipynb
│   ├── 4-SPARQL
│   │   ├── perform_queries.py
│   │   ├── sparql2_127results.csv
│   │   ├── sparql3_140results-all-prices-test.csv
│   │   ├── sparql3_1results.csv
│   │   ├── sparql4_669results.csv
│   │   └── sparql5_16results.csv
│   ├── 5-OA
│   │   ├── all_files_with_reasoning_oa2_1.ttl
│   │   ├── calculate_equivalences.py
│   │   ├── equivalence_triples_oa1-good.ttl
│   │   ├── equivalence_triples_oa1.ttl
│   │   ├── hermit_reasoner_results_equivalence_triples_oa1_oa2_2.txt
│   │   ├── hermit_reasoner_results_pizza_manchester_oa2_2.txt
│   │   ├── hermit_reasoner_results_pizza_restaurant_ontology9_oa2_2.txt
│   │   ├── load_ontology.py
│   │   ├── onto_access.py
│   │   ├── ontologies
│   │   │   ├── equivalence_triples_oa1.ttl
│   │   │   ├── pizza_manchester.owl
│   │   │   ├── pizza_restaurant_ontology9.owl
│   │   │   └── pizza_restaurant_ontology9.ttl
│   │   └── results.log
│   ├── 6-VECTOR
│   │   ├── Standalone_01
│   │   │   ├── OWL2Vec_Standalone.py
│   │   │   ├── cache
│   │   │   │   ├── annotations.txt
│   │   │   │   ├── axioms.txt
│   │   │   │   ├── document_sentences.txt
│   │   │   │   ├── entities.txt
│   │   │   │   └── projection.ttl
│   │   │   ├── config1.cfg
│   │   │   ├── config2.cfg
│   │   │   ├── config3.cfg
│   │   │   ├── default.cfg
│   │   │   ├── lib
│   │   │   │   ├── Evaluator.py
│   │   │   │   ├── Graph_for_OpenKE.py
│   │   │   │   ├── Label.py
│   │   │   │   ├── Onto_Access.py
│   │   │   │   ├── Onto_Annotations.py
│   │   │   │   ├── Onto_Projection.py
│   │   │   │   └──  RDF2Vec_Embed.py
│   │   │   ├── output_embedding
│   │   │   │   ├── config1.embeddings
│   │   │   │   ├── config1.embeddings.bin
│   │   │   │   ├── config1.embeddings.txt
│   │   │   │   ├── config2.embeddings
│   │   │   │   ├── config2.embeddings.bin
│   │   │   │   ├── config2.embeddings.txt
│   │   │   │   ├── config3.embeddings
│   │   │   │   ├── config3.embeddings.bin
│   │   │   │   ├── config3.embeddings.txt
│   │   │   │   ├── load_embeddings.py
│   │   │   │   ├── output
│   │   │   │   ├── pizza.embeddings
│   │   │   │   ├── pizza.embeddings.bin
│   │   │   │   ├── pizza.embeddings.model
│   │   │   │   └── pizza.embeddings.txt
│   │   │   ├── pizza.owl
│   │   │   ├── pizza_restaurants_with_reasoning_sparql1.rdf
│   │   │   └── rdf2vec
│   │   │       ├── __init__.py
│   │   │       ├── converters.py
│   │   │       ├── create_embeddings.py
│   │   │       ├── embed.py
│   │   │       ├── example.py
│   │   │       ├── experiment.sh
│   │   │       ├── graph.py
│   │   │       └── walkers
│   │   ├── cluster_embeddings.ipynb
│   │   └── inspect_similarity.py
│   ├── data
│   │   ├── INM713_coursework_data_pizza_8358_1_reduced.csv
│   │   ├── data_pizza_bianca_white_test.csv
│   │   ├── data_pizza_margherita_test.csv
│   │   ├── data_pizza_minimum_test.csv
│   │   ├── data_pizza_no_postcode_test.csv
│   │   ├── data_pizza_preprocessing_test.csv
│   │   ├── data_pizza_shared_restaurant_name_test.csv
│   │   └── pizza_manchester.owl
│   └──images
│       └── pizza_restaurant_ontology8.png
└── tasks.py
```