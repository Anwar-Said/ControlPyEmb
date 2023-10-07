from ControlPyEmb.ctrl import get_ctrl_emb
import networkx as nx
import numpy as np

g1 = nx.fast_gnp_random_graph(50, 0.1)
emb1 = list(get_ctrl_emb(g1).values()) ### get_ctrl_emb returns a dictionary containing each metric with values

g2 = nx.fast_gnp_random_graph(50, 0.8)
emb2 = list(get_ctrl_emb(g2).values())

print(np.linalg.norm(np.array(emb1)-np.array(emb2)))













