# GTUT Python Implementation
___

 Run the following commands in order:
- `python formatdata.py` which will collect and store the data in different 
data structures to be used later down the pipeline
- `python resolve_data_conflicts.py` to resolve data conflicts, and generate 
`.bigraph` files which will consist of edgelists of users to articles
- `python preprocess_data.py` in the `biclique` folder. This will preprocess 
the information before finding the maximal bicliques.
- `python generate_maximal_quasi_bicliques.py` to identify the maximal 
bicliques in our graphical structure

Now that the bicliques have been identified, we can proceed with the steps of the
GTUT algorithm.
- `python phase1.py`
- `python phase2.py`
- `python phase3.py`
