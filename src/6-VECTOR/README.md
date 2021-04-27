# 6 - Task OE (Ontology Embedding)

The most up-to-date ontology in use for the rest of the project is [../1-OWL/pizza_restaurant_ontology8.ttl](../1-OWL/pizza_restaurant_ontology8.ttl), and the corresponding code is in the [ontology8](ontology8/) folder.

The code to run for Subtask OE.1 is in this file: [Standalone_01/OWL2Vec_Standalone.py](Standalone_01/OWL2Vec_Standalone.py) (replace config file argument as you like)

```bash
python Standalone_01/OWL2Vec_Standalone.py --ontology_file pizza_restaurants_with_reasoning_sparql1.rdf --config_file Standalone_01/config1.cfg
```

The config files are at:
- [Standalone_01/config1.cfg](Standalone_01/config1.cfg)
- [Standalone_01/config2.cfg](Standalone_01/config2.cfg)
- [Standalone_01/config3.cfg](Standalone_01/config3.cfg)

The code to run for Subtask OE.2 is in this file: [inspect_similarity.py](inspect_similarity.py)

To run this, comment/uncomment the snippets in the file's `main` method to run the tasks:

```bash
python inspect_similarity.py
```

The code to run for Subtask OE.3 is in this file: [cluster_embeddings.ipynb](cluster_embeddings.ipynb). Just open and run.
