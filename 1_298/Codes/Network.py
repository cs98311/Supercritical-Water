#! /usr/bin/env python3

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


nodes = np.loadtxt("SysInfo.txt")[1].astype(int)
nodes = [i for i in range(0, nodes)]

edges = np.genfromtxt(r"Water/Edges.csv", delimiter=",", dtype=int)

G = nx.Graph()
G.add_nodes_from(nodes, nodetype=int)
G.add_edges_from(edges, edgetype=int)


# HBpercent
degree = [v for k, v in nx.degree(G)]
heights, bins, plot = plt.hist(degree, bins=range(7), edgecolor="k")
new_heights = 100 * heights / heights.sum()

with open("Water/HBpercent.txt", "a") as f:
    print(*np.round(new_heights, 4), file=f)


# Clusters
components = list(nx.connected_components(G))
components = list(sorted(components, key=lambda x: len(x), reverse=True))

comp_sizes = []
for comp in components:
    comp_sizes.append(len(comp))


prob = np.zeros(10)

for i in comp_sizes:
    if i == 1:
        prob[0] += i
    elif i == 2:
        prob[1] += i
    elif i == 3:
        prob[2] += i
    elif i == 4:
        prob[3] += i
    elif i >= 5 and i <= 20:
        prob[4] += i
    elif i >= 21 and i <= 50:
        prob[5] += i
    elif i >= 51 and i <= 100:
        prob[6] += i
    elif i >= 101 and i <= 300:
        prob[7] += i
    elif i >= 301 and i <= 500:
        prob[8] += i
    elif i >= 501:
        prob[9] += i


prob = prob * 100 / nx.number_of_nodes(G)

heights, bins, plot = plt.hist(
    comp_sizes, bins=[*range(1, 5), 20, 50, 100, 300, 500, 600]
)
with open("Water/ClusterFreq.txt", "a") as f:
    print(*heights, file=f)

with open("Water/ClusterPerc.txt", "a") as f:
    print(*np.round(prob, 4), file=f)


# Cycles
cycles = nx.cycle_basis(G)
sizes = [len(x) for x in cycles]
sizes = np.array(sizes)
sizes = -np.sort(-sizes)


if sizes.size:
    with open("Water/Cycles.txt", "a") as f:
        print(*sizes, file=f)

    prob = np.zeros(11)

    for i in sizes:
        if i < 11:
            prob[i] += 1

    prob = prob / len(sizes)
    prob = prob[3:]

    with open("Water/CyclesProbs.txt", "a") as f:
        print(*np.round(prob, 4), file=f)


# with open('Water/ClusterCoeff.txt','a') as f:
#     print(nx.cluster.average_clustering(G), file =f)


components = nx.connected_components(G)
largest_component = max(components, key=len)
LCC = G.subgraph(largest_component)

# with open('Water/SPL.txt','a') as f:
#     print(nx.average_shortest_path_length(LCC), file =f)


with open("Water/LCC.txt", "a") as f:
    print(len(LCC), file=f)
