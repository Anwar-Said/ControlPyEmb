Introduction by Example
================================

We will briefly introduce the fundamental concepts of ControlPyEmb through self-contained examples. 


Computing Embeddings 
----------------------------------

.. code-block:: python
    :linenos:

    from ControlPyEmb.ctrl import get_ctrl_emb
    import networkx as nx
    import numpy as np

    g1 = nx.fast_gnp_random_graph(50, 0.1) # generate a sparse random graph
    emb1 = list(get_ctrl_emb(g1).values()) ### get_ctrl_emb returns a dictionary containing the metrics with their corresponding values
 
    g2 = nx.fast_gnp_random_graph(50, 0.8) # generate a dense random graph
    emb2 = list(get_ctrl_emb(g2).values()) # extract embedding

    np.linalg.norm(np.array(emb1)-np.array(emb2)) ### compare the two embeddings
   


