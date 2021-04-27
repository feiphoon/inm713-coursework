# 3 - Task RDF (Tabular Data to Knowledge Graph)

The most up-to-date ontology in use for the rest of the project is [../1-OWL/pizza_restaurant_ontology8.ttl](../1-OWL/pizza_restaurant_ontology8.ttl), and the corresponding code is in the [ontology8](ontology8/) folder.

The code to run for Subtasks RDF.2, RDF.3 and SPARQL.1 is in: [ontology8/create_rdf_triples.py](ontology8/create_rdf_triples.py)

To run this, comment/uncomment the following variables in the file's `main` method to run the tasks, like so:

```python
# Comment these out to run each task
TASK: Task = Task.RDF2
# TASK: Task = Task.RDF3
# TASK: Task = Task.SPARQL1
```

Then run

```bash
python ontology8/create_rdf_triples.py
```

Results for Subtask RDF.2 and RDF.3:
- [ontology8/pizza_restaurants_without_reasoning_rdf2.ttl](ontology8/pizza_restaurants_without_reasoning_rdf2.ttl)
- [ontology8/pizza_restaurants_without_reasoning_rdf3.ttl](ontology8/pizza_restaurants_without_reasoning_rdf3.ttl)

Results for Subtask SPARQL.1 (next task):
- [ontology8/pizza_restaurants_with_reasoning_sparql1.ttl](ontology8/pizza_restaurants_with_reasoning_sparql1.ttl)
