"""
Author Gabryxx7: 01-Aug-2021
"""

from networkx.generators.ego import ego_graph
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.ticker as ticker
import seaborn as sns
import matplotlib.dates as mdates
import datetime as dt
from dateutil import tz
import sys, os
from importlib import reload  
from IPython.display import display, HTML, display_html
from itertools import chain,cycle
from operator import itemgetter
import networkx as nx
from networkx.algorithms import community
from itertools import combinations
import networkx as nx
from matplotlib.pyplot import figure
from multiprocessing.dummy import Pool as ThreadPool
import utils
import backbone
import base64
import random

class EgoNetworkAnalyzer():

    def __init__(self, pandas_edge_list, from_col, to_col, weight_col=None, ego_radius=2, alpha_threshold=-1):
        self.weight_col = weight_col
        self.edge_list = pandas_edge_list
        self.from_col = from_col
        self.to_col = to_col
        self.full_network_key = "full_network"
        self.full_network_bb_key = "full_network_backboned"
        self.networks_data = None
        self.backboned = False
        self.alpha_threshold = alpha_threshold
        self.ego_radius = ego_radius

    def make_full_network(self, backboning=False, alpha_threshold=0.04):  
        self.networks_data = {}
        if self.weight_col:
            full_network = nx.from_pandas_edgelist(self.edge_list, edge_attr=self.weight_col, source=self.from_col, target=self.to_col) 
        else:
            full_network = nx.from_pandas_edgelist(self.edge_list, source=self.from_col, target=self.to_col) 

        self.networks_data[self.full_network_key] = {}
        self.networks_data[self.full_network_key]["network"] = full_network
        self.networks_data[self.full_network_key]["total_nodes"] = full_network.number_of_nodes()
        self.networks_data[self.full_network_key]["total_edges"] = full_network.number_of_edges()

        print(f"Full Network: nodes = {self.networks_data[self.full_network_key]['total_nodes']}, edges = {self.networks_data[self.full_network_key]['total_edges']}")
        if backboning:
            full_network = backbone.disparity_filter(full_network, weight=self.weight_col)
            full_network = nx.Graph([(u, v, d) for u, v, d in full_network.edges(data=True) if d['alpha'] < alpha_threshold])    
            self.networks_data[self.full_network_bb_key] = {}        
            self.networks_data[self.full_network_bb_key]["network"] = self.full_network
            self.networks_data[self.full_network_bb_key]["total_nodes"] = full_network.number_of_nodes()
            self.networks_data[self.full_network_bb_key]["total_edges"] = full_network.number_of_edges()
            self.networks_data[self.full_network_bb_key]["alpha_threshold"] = alpha_threshold
            self.networks_data[self.full_network_bb_key]["backboned"] = backboning
            print(f"Backboned network: nodes = {self.networks_data[self.full_network_key]['total_nodes']}, edges = {self.networks_data[self.full_network_key]['total_edges']}")

        return self.networks_data

    def encrypt_df(self, df, cols_to_encrypt, key):
        df[cols_to_encrypt] = df[cols_to_encrypt].applymap(lambda x: self.encrypt(key,x))
        return df
    
    def decrypt_df(self, df, cols_to_decrypt, key):
        df[cols_to_decrypt] = df[cols_to_decrypt].applymap(lambda x: self.decrypt(key,x))
        return df
        
    def encrypt(self, key, plaintext):
        cipher = XOR.new(key)
        return base64.b64encode(cipher.encrypt(plaintext))

    def decrypt(self, key, ciphertext):
        cipher = XOR.new(key)
        return cipher.decrypt(base64.b64decode(ciphertext))

    def print_nodes_list(self, G):
        print(self.get_nodes_string(G))
            
    def get_nodes_string(self, G):
        string = ""
        i = 0
        for node in G.nodes:
            string += f"{i} - {node}\n"
            i +=1    
        return string
            
    def get_bidirectional_connections(self, G):
        biconnections = set()
        for u, v in G.edges():
            if u > v:  # Avoid duplicates, such as (1, 2) and (2, 1)
                v, u = u, v
            if self.have_bidirectional_relationship(G, u, v):
                biconnections.add((u, v))
        return biconnections
    
    def have_bidirectional_relationship(self, G, node1, node2):
        return G.has_edge(node1, node2) and G.has_edge(node2, node1)

    def print_bidirectional_connections(self, G):
        bidirections = self.get_bidirectional_connections(G)
        i = 0
        for edge in bidirections:
            print(f"{i} - {edge}")
            i += 1
            
    def get_id_from_name(self, name, id_name_dict):
        for key, val in id_name_dict:
            if val == name:
                return key
        return None

    def get_name_from_id(self, id, id_name_dict):
        return id_name_dict[id]

    def get_ego_network_data(self, full_network, ego_node, radius=2):
        ego_net = {}
        ego_net["ego"] = ego_node
        if self.weight_col is None:
            ego_net["network"] = nx.ego_graph(full_network, ego_node, undirected=True, radius=radius)
        else:
            ego_net["network"] = nx.ego_graph(full_network, ego_node, undirected=True, radius=radius, distance=weight_col)
        ego_net["total_nodes"] = ego_net["network"].number_of_nodes()
        ego_net["total_edges"] = ego_net["network"].number_of_edges()
        if self.weight_col is None:
            ego_net["ego_node_degree"] = ego_net["network"].degree(ego_node)
        else:
            ego_net["ego_node_degree"] = ego_net["network"].degree(ego_node, weight=weight_col)
        return ego_net

    def get_all_ego_networks_data(self, radius=2):
        i = 0
        if self.weight_col is None:
            print(f"Networks are undirected, unweighted, using radius {radius}")
        else:
            print(f"Networks are undirected, with weight attr {self.weight_col}, using radius {radius}")

        for ego_node in self.full_network.nodes:
            ego_net = self.get_ego_network_data(self.full_network, ego_node, radius=radius)                
            print(f'\n {utils.formatted_now(sepDate="-", sepTime=":", sep=" ")}\t Network for \t {i} - {ego_node}, total nodes: {ego_net["total_nodes"]}, edges: {ego_net["total_edges"]}')
            i += 1
            self.networks_data[ego_node] = ego_net
        return self.networks_data

    def triads(self, m):
        out = {0: set(), 1: set(), 2: set(), 3: set()}
        nodes = list(m.keys())
        for i, (n1, row) in enumerate(m.items()):
    #         print(f"--> Row {i + 1} of {len(m.items())} <--")
            # get all the connected nodes = existing keys
            for n2 in row.keys():
                # iterate over row of connected node
                for n3 in m[n2]:
                    # n1 exists in this row, all 3 nodes are connected to each other = type 3
                    if n3 in row:
                        if len({n1, n2, n3}) == 3:
                            t = tuple(sorted((n1, n2, n3)))
                            out[3].add(t)
                    # n2 is connected to n1 and n3 but not n1 to n3 = type 2
                    else:
                        if len({n1, n2, n3}) == 3:
                            t = tuple(sorted((n1, n2, n3)))
                            out[2].add(t)
                # n1 and n2 are connected, get all nodes not connected to either = type 1
                for n3 in nodes:
                    if n3 not in row and n3 not in m[n2]:
                        if len({n1, n2, n3}) == 3:
                            t = tuple(sorted((n1, n2, n3)))
                            out[1].add(t)
            for j, n2 in enumerate(nodes):
                if n2 not in row:
                    # n2 not connected to n1
                    for n3 in nodes[j+1:]:
                        if n3 not in row and n3 not in m[n2]:
                            # n3 is not connected to n1 or n2 = type 0
                            if len({n1, n2, n3}) == 3:
                                t = tuple(sorted((n1, n2, n3)))
                                out[0].add(t)
        return out

    def calculate_simmelian_ties(self, ego_network_data):
        ego = ego_network_data["ego"]
        ego_network = ego_network_data["network"]
        m = nx.convert.to_dict_of_dicts(ego_network)
        triads_res = self.triads(m)
    #     print(triads_res)
        res = {}    
        for index in triads_res:
            res["total"+str(index)+"_triads"] = len(triads_res[index])
            res["triads"+str(index)+"_ego"] = 0
            for triad in triads_res[index]:
                if ego in triad:
    #                 print(f"Triad: \t{triad}m Ego:\t {ego}, Set: \t{index}")
                    res["triads"+str(index)+"_ego"] += 1   
            res["simmelian_ties"+str(index)] = -1
            if res["total"+str(index)+"_triads"]> 0:
                res["simmelian_ties"+str(index)] =res["triads"+str(index)+"_ego"] / res["total"+str(index)+"_triads"]
        return res


    # Burt's formula
    # https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.structuralholes.local_constraint.html#networkx.algorithms.structuralholes.local_constraint
    def calculate_constraints(self, ego_network_data):
        total_constraints = -1
        eff_size = -1
        ego = ego_network_data["ego"]
        ego_network = ego_network_data["network"]
        if self.weight_col is None:
            total_constraints = nx.constraint(ego_network, nodes = [ego])
            eff_size = nx.effective_size(ego_network, nodes = [ego])
        else:
            total_constraints = nx.constraint(ego_network, nodes = [ego], weight=self.weight_col)
            eff_size = nx.effective_size(ego_network, nodes = [ego], weight=self.weight_col)
        size = list(eff_size.values())[0]
        constr = list(total_constraints.values())[0]
        log_constr = np.log(constr)
        return {"constraints_sum": constr, "logn_constraints":log_constr, "effective_size": size}

    # Calculate the degree centrality 
    # def calculate_status(ego_network, ego):
    #     total_degree = 0
    #     for node in ego_network.nodes:
    #         if ego not in node:
    #             total_degree += constraint[1]    
    #     return {"constraints_sum": total_c, "logn_constraints":constr}

    def run_network_metrics(self, ego_node):
        print(f'\n {utils.formatted_now(sepDate="-", sepTime=":", sep=" ")}\t Starting ego network metrics calculation for \t {ego_node}, ego network calculated? {ego_node in self.networks_data}')        
        if ego_node in self.networks_data:
            ego_data = self.networks_data[ego_node]
        else:
            if self.backboned:
                ego_data = self.get_ego_network_data(self.networks_data[self.full_network_bb_key]["network"], ego_node)  
            else:
                ego_data = self.get_ego_network_data(self.networks_data[self.full_network_key]["network"], ego_node)                
        
        ties = self.calculate_simmelian_ties(ego_data)
        ego_data.update(ties)
        constraints = self.calculate_constraints(ego_data)
        ego_data.update(constraints)
        self.networks_data[ego_node] = ego_data            
        print(f'\n {utils.formatted_now(sepDate="-", sepTime=":", sep=" ")}\t COMPLETED ego network metrics calculation for \t {ego_node}')
        return self.networks_data

    def calculate_ego_networks_metrics(self, backboning=False, multi_thread=True, n_threads=23, alpha_threshold=0.04):
        if self.networks_data is None:
            print(f'{utils.formatted_now(sepDate="-", sepTime=":", sep=" ")}\t Calculating full network first...')
            self.make_full_network(backboning, alpha_threshold)           
        results = []
            
        if self.backboned:
            network = self.networks_data[self.full_network_bb_key]["network"]
        else:
            network = self.networks_data[self.full_network_key]["network"]
        node_list = network.nodes
        num_tasks = len(node_list)

        print(f'{utils.formatted_now(sepDate="-", sepTime=":", sep=" ")}\t Starting {"MULTI" if multi_thread else "SINGLE"} threaded ego networks metrics calculation, backboned? {self.backboned}')
        if multi_thread:
            pool = ThreadPool(n_threads) 
            for i, res in enumerate(pool.imap_unordered(self.run_network_metrics, node_list), 1):
                print(f'\nDone {i}/{num_tasks}\t {(i/num_tasks) * 100}%\n')
                print(res)
                results.append(res)
        #     results = pool.map(run_network_metrics, ego_networks["egonetworks"])
            return results
        else:
            i = 1
            for node in node_list:
                res = self.run_network_metrics(node)
                print(f'\nDone {i}/{num_tasks}\t {(i/num_tasks) * 100}%\n')
                i += 1
                results.append(res)
        return results
        
    