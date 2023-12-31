import controlpy
import networkx as nx
import numpy.linalg as LA
import numpy as np

def get_ctrl_emb(G,num_iterations = 30):
    """control-based graph embedding from `"Network Controllability Perspectives on Graph Representation"` paper.  

    Args:
        G (networkx): a networkx graph
        num_iterations (int, optional): number of iterations to be repeated. Defaults to 30.
        Return: Embedding vector

    """

    G = nx.convert_node_labels_to_integers(G)
    if not nx.is_connected(G):
        G = add_vertex(G)

    if G.number_of_nodes()<10:
#         return list(np.zeros(162, dtype = float))
        G = add_multiple_copies(G)
    A1 = -(np.matrix(nx.laplacian_matrix(G,nodelist=sorted(G.nodes())).todense()))
    n = A1.shape[0]
    desc = {}
    leaders = []
    for num_l_idx, num_leaders in enumerate([1,2,5,9,int(n*2/100)+1,int(n*5/100)+1,int(n*10/100)+1,int(n*20/100)+1,int(n*30/100)+1]):
#         A1 = np.matrix( nx.laplacian_matrix(G).todense() )
        old_n = A1.shape[0]
        traces = []
        ranks = []
        min_eigs = []
        max_eigs = []
        metric_dimension = []
        for i in range(num_iterations):
            follows = np.random.choice(old_n,old_n-num_leaders,replace=False)
            leaders = list(set(range(old_n))-set(follows))
            A2 = A1[follows, :]
            A3 = A2[:, follows]
            A = 1*A3
            n = A.shape[0]
            mask = np.ones(old_n, dtype=bool)
            mask[leaders] = False
            B = A1[mask,:] #removing corresponding rows of leaders from laplacian
            B = B[:,leaders] #selecting corresponding columns of leaders from laplacian
            A = np.mat(A)
            B = np.mat(B)
            
            grm = controlpy.analysis.controllability_gramian(A,B)
            rnk = LA.matrix_rank(grm)
            ranks.append(rnk)
            traces.append( np.trace(grm) )
            
            w, v = LA.eig(grm)
            a = np.real(w)
            a[a == 0] = 0.0001
            minval = np.min(a)
            min_eigs.append( minval ) 
            max_eigs.append(np.max( a ) )

                       
            metric_dimension.append(compute_metric_dimension(G, leaders))

        
        desc['GRM_MAX_TRACE_'+str(num_l_idx)] = np.max(traces)
        desc['GRM_MIN_TRACE_'+str(num_l_idx)] = np.min(traces) 
        desc['GRM_MAX_RANK_'+str(num_l_idx)]  = np.max(ranks) 
        desc['GRM_MIN_RANK_'+str(num_l_idx)]  = np.min(ranks) 
            

        desc['GRM_MAX_of_MIN_EIG_'+str(num_l_idx)] = np.max(min_eigs)
        desc['GRM_MIN_of_MIN_EIG_'+str(num_l_idx)] = np.min(min_eigs)

        desc['GRM_MAX_of_MAX_EIG_'+str(num_l_idx)] = np.max(max_eigs)
        desc['GRM_MIN_of_MAX_EIG_'+str(num_l_idx)] = np.min(max_eigs)
                

        
        desc['GRM_MEAN_TRACE_'+str(num_l_idx)] = np.mean(traces)
        desc['GRM_MEAN_RANK_'+str(num_l_idx)] = np.mean(ranks)

            
        desc['GRM_MEAN_MAX_EIG_'+str(num_l_idx)] = np.mean(max_eigs)
        desc['GRM_MEAN_MIN_EIG_'+str(num_l_idx)] = np.mean(min_eigs)

        desc['METRIC_DIMENSION_MEAN'+str(num_l_idx)] = np.mean(metric_dimension)
        desc['METRIC_DIMENSION_MIN'+str(num_l_idx)] = np.min(metric_dimension)
        desc['METRIC_DIMENSION_MAX'+str(num_l_idx)] = np.max(metric_dimension)

    n,m = G.number_of_nodes(),G.number_of_edges()
    desc['no_nodes'] = n
    desc['no_edges'] = m
    desc['no_bi_conn_comp'] =len(list(nx.biconnected_components(G)))
    
    Ls = sorted(nx.laplacian_spectrum(G))
    desc['LS_0'] = Ls[0]
    desc['LS_1'] = Ls[1]
    desc['LS_2'] = Ls[2]
    
    desc['LSE_3'] = Ls[3]
    desc['LSE_4'] = Ls[4]
    desc['LSE_-1'] = Ls[-1]
    desc['LSE_-2'] = Ls[-2]
    desc['LSE_-3'] = Ls[-3]
    
    if n-m == 1:
        desc['0cyc'] = 1  
    else:
        desc['0cyc'] = 0
    if n-m == 0:
        desc['1cyc'] = 1
    else:
        desc['1cyc'] = 0
    if n-m == -1:
        desc['2cyc'] = 1
    else:
        desc['2cyc'] = 0
    if n-m < -1:
        desc['g2cyc'] = 1
    else:
        desc['g2cyc'] = 0

    desc.update(add_features(G))
    return(desc)
def add_multiple_copies(G):
    no_node = G.number_of_nodes()   
    H = G.copy()
    H = nx.convert_node_labels_to_integers(H, ordering='sorted')
    val = sorted(G.nodes())
    val0 = val[0]
    while H.number_of_nodes()<10:
        val1 = H.number_of_nodes()-1
        H = nx.union(H, G, rename=('G1-', 'G2-'))
        H.add_edge('G1-'+str(val1), 'G2-'+str(val0))
        H = nx.convert_node_labels_to_integers(H, ordering='sorted')
    return H

def trace_deq_seq(G):
    seq = sorted(list(dict(nx.degree(G)).values()),reverse = False)
    trc = 0
    for idx, i in enumerate(seq):
        if idx+1<=i:
            trc = idx+1
    return trc

def add_features(G):
    L = nx.laplacian_matrix(G).todense()
    eig = LA.eigvals(L)
    avg_deg = 2*(G.number_of_edges()/G.number_of_nodes()) # made it faster
    lap_energy = sum([abs(i-avg_deg) for i in eig])
    dist_matrix =np.array(nx.floyd_warshall_numpy(G,nodelist=sorted(G.nodes()))) #nodelist, important argument, I will let you know
    eccentricity = dist_matrix * (dist_matrix >= np.sort(dist_matrix, axis=1)[:,[-1]]).astype(int) #can be computed through networkx thats why nodelist argument is added
    e_vals = LA.eigvals(eccentricity) 
    largest_eig = np.real(max(e_vals))
    energy = np.real(sum([abs(x) for x in e_vals]))
    wiener_index = nx.wiener_index(G)
    trace_DS = trace_deq_seq(G)  #it was different then your implementation kindly read the document again as sent by the dr. Waseem or go through by my implementation
    return {'lap_energy':lap_energy,'ecc_spectrum':largest_eig,'ecc_energy':energy,'wiener_index':wiener_index,'trace_deg_seq':trace_DS}

def compute_metric_dimension(G, leaders):
    nodes_list = list(G.nodes()) 
    distance_vec = []
    for n in nodes_list:
        v_ = [nx.shortest_path_length(G, source=n, target=l) for l in leaders]
        distance_vec.append(v_)
    distance_vec = np.array(distance_vec)
    return np.unique(distance_vec, axis=0).shape[0]

        
def add_vertex(G):
    G = nx.convert_node_labels_to_integers(G)
    nodes = sorted(list(G.nodes()))
    new_vertex = nodes[-1]+1 
    G.add_node(new_vertex)
    for n in G.nodes():
        if n !=new_vertex:
            G.add_edge(new_vertex, n)
    return G