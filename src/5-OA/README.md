# 5 - Task OA (Ontology Alignment)

The most up-to-date ontology in use for the rest of the project is [../1-OWL/pizza_restaurant_ontology8.ttl](../1-OWL/pizza_restaurant_ontology8.ttl), and the corresponding code is in the [ontology8](ontology8/) folder.


The code to run for Subtasks OA.1, and OA.2 is in this file: [calculate_equivalences.py](calculate_equivalences.py)

There are two alternatives to running Subtask OA.2 - these are marked differently below.

To run this, comment/uncomment the following variables in the file's `main` method to run the tasks, like so:

```python
# Comment these out to run each task
TASK: Task = Task.OA1.value
# TASK: Task = Task.OA2_1.value
# TASK: Task = Task.OA2_2.value
```

Then run

```bash
python calculate_equivalences.py
```

Results for Subtask QA.1:
- [equivalence_triples_oa1.ttl](equivalence_triples_oa1.ttl)

Results for Subtask OA.2 (alternative 1):
- [all_files_with_reasoning_oa2_1.ttl](src/5-OA/all_files_with_reasoning_oa2_1.ttl)


Results for Subtask OA.2 (alternative 2):
- [hermit_reasoner_results_equivalence_triples_oa1_oa2_2.txt](hermit_reasoner_results_equivalence_triples_oa1_oa2_2.txt)
- [hermit_reasoner_results_pizza_manchester_oa2_2.txt](hermit_reasoner_results_pizza_manchester_oa2_2.txt)
- [hermit_reasoner_results_pizza_restaurant_ontology9_oa2_2.txt](hermit_reasoner_results_pizza_restaurant_ontology9_oa2_2.txt)