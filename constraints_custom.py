import random
import networkx as nx

"""
Author Gabryxx7
I was not sure the networkx cosntraints() function was returning what I needed so I re-implemented it myself
"""

def get_weight(G,i,j,weight_attr=None):
    if weight_attr is None:
        return int(G.has_edge(i, j))
    try:
        return G[i][j][weight_attr]
    except:
        return 0
"""
Calculated as per paper's explanation:
> The notion of “time and energy” is thus specifiedas a weight
> zij between a pair of users, which could also be binary, like in our case where zij = 1 iff there exists an edge (i; j).
I'm using has_edge() to get the binary value
"""
def normalized_weight(G, i, j, weight_attr=None):
    zij = get_weight(G,i,j,weight_attr)
    debug_str = f"{zij}/"
    sum_ziq = 0
    for q in G.nodes:
        ziq = get_weight(G,i,q,weight_attr)      
        sum_ziq += ziq
    debug_str += f"{sum_ziq}"
    if sum_ziq > 0:
#         debug_str += str(zij/sum_ziq)
#         display(debug_str)
        return zij/sum_ziq, debug_str
#     debug_str += "0"
#     display(debug_str)
    return 0, debug_str
  
"""
From Networkx (https://networkx.org/documentation/stable/reference/classes/generated/networkx.Graph.adj.html)
> G.adj: Graph adjacency object holding the neighbors of each node.
"""
def neighbors(G, i):
#     display(f"Neighbors of: {i}\t {G.adj[i]}")
    return G.adj[i]

"""
This is pretty much Burt's formulation for local constraints: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.structuralholes.local_constraint.html
more precisely, the local constraint on i with respect to j, we'll name it C_ij can be calculated as:

C_ij= (P_ij + SUM^{q in N(j)}(P_iq * P_qj))^2

Where P_ij = Z_ij/SUM^{q in nodes(G)}(Z_iq)

So P is the normalized weight between i and j.
The normalization is quite simple, just take the weight of the edge i-j and divide it by the sum of the edges between i and any other node
"""

def burt_node_constraint(G, i, j, weight_attr=None):
    direct, fraction = normalized_weight(G, i, j, weight_attr)
    debug_str = f"| {i} Degree: {G.degree(i, weight='weight')}, {j} Degree: {G.degree(j, weight='weight')}, P.{i}{j}={fraction}={direct} + ( "
    indirect = 0
    for q, val in neighbors(G, j).items():
        if q != i and q != j:
            ziq, fractioniq = normalized_weight(G, i, q, weight_attr)
            zqj, fractionqj = normalized_weight(G, q, j, weight_attr)
            indirect += ziq*zqj
            fraction = fractioniq + "*" + fractionqj
            debug_str += f"P.{i}{q}*P.{q}{j}={fraction}={ziq*zqj} + "
    debug_str += " )"
    # print(f"C.{i}{j}={(direct + indirect) ** 2 }= {debug_str}")
    return (direct + indirect) ** 2 
    
def custom_constraints(G, nodes=None, weight_attr=None):
    constraints = {}
    neighborhood = {}
    if nodes is None:
        nodes = G.nodes
    for i in nodes:
        constraints[i] = 0
        neighborhood[i] = "["
        for j, val in neighbors(G, i).items():
            constraints[i] += burt_node_constraint(G, i, j, weight_attr)
            neighborhood[i] += str(j)+", "
        neighborhood[i] += "]"
        # print(f"Neighborhood of {i}: {neighborhood[i]}")
#         for j in G.nodes:
#             if i != j:
#                 constraints[i] += local_constraint(G, i, j)
    return constraints     
