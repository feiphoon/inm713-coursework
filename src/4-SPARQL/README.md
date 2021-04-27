# 4 - Task SPARQL (SPARQL and Reasoning)

The most up-to-date ontology in use for the rest of the project is [../1-OWL/pizza_restaurant_ontology8.ttl](../1-OWL/pizza_restaurant_ontology8.ttl), and the corresponding code is in the [ontology8](ontology8/) folder.

The code to run for Subtasks SPARQL.1 is in the previous task's folder: [../3-RDF/ontology8/create_rdf_triples.py](../3-RDF/ontology8/create_rdf_triples.py)

To run this, comment/uncomment the following variables in the file's `main` method to run the tasks, like so:

```python
# Comment these out to run each task
# TASK: Task = Task.RDF2
# TASK: Task = Task.RDF3
TASK: Task = Task.SPARQL1
```

Then run

```bash
python ../3-RDF/ontology8/create_rdf_triples.py
```

The code to run for Subtasks SPARQL.2, SPARQL.3, SPARQL.4, and SPARQL.5 is in this file: [perform_queries.py](perform_queries.py)

To run this, comment/uncomment the following variables in the file's `main` method to run the tasks, like so:

```python
# Comment these out to run each task
TASK: Task = Task.SPARQL2.value
# TASK: Task = Task.SPARQL3.value
# TASK: Task = Task.SPARQL4.value
# TASK: Task = Task.SPARQL5.value
```

Then run

```bash
python perform_queries.py
```

Results for Subtask SPARQL.2 to SPARQL.5 (the number of results returned is in the name of the file):
- [sparql2_127results.csv](sparql2_127results.csv)
- [sparql3_1results.csv](sparql3_1results.csv)
- [sparql4_669results.csv](sparql4_669results.csv)
- [sparql5_16results.csv](sparql5_16results.csv)
