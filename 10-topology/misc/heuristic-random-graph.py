#!/usr/bin/env python3
# coding: utf-8
#====================================================================
#
# generate heuristic solution to order degree problem
# by Robert Waniek
# 2021
# "create-heur-randCS.py" is licensed under a
# Creative Commons Attribution 4.0 International License.
# http://creativecommons.org/licenses/by/4.0/
#
# based on create-random.py (Create a random graph)
# by Ikki Fujiwara, National Institute of Informatics
# 2018-11-12
# "create-random.py" is licensed under a
# Creative Commons Attribution 4.0 International License.
# http://creativecommons.org/licenses/by/4.0/
#
# CHANGELOG:
# separated script features (creation, statistics, rendering)
# minor feature: added naive support for uneven nodes*degree
# improved feature: support for uneven nodes*3 via cycle-star-graph
# minor feature: handle trivial cases
# minor use case: order-degree-assertion on generated graph
#
#====================================================================
import networkx
import argparse
import math
import numpy
import sys

########## BASICS ##########
argumentparser = argparse.ArgumentParser()
argumentparser.add_argument('nodes', type=int)
argumentparser.add_argument('degree', type=int)
def main(args):
    ########## PARSE PARAMETERS ##########
    nodes = args.nodes
    degree = args.degree
    ########## HANDLE TRIVIAL CASES ##########
    if nodes < 1:
        sys.exit("trivial solution: no graph")

    if degree < 2:
        sys.exit("trivial solution: no connected graph available")
    if nodes == 2:
        sys.exit("trivial solution: 0 -- 1")
    if degree == 2:
        sys.exit("trivial solution: cycle or not connected")
    if nodes <= degree+1:
        sys.exit("trivial solution: complete graph")
    assert nodes >= 5
    assert degree >= 3

    ########## GENERATE GRAPH ##########
    #basic case: standard random regular graph exists
    if degree * nodes % 2 == 0:
        graph = networkx.random_regular_graph(degree, nodes, 0)
    #edge case heuristic: nodes*3 % 2 == 1
    elif degree == 3: # and degree * nodes % 2 == 1
        graph = generate_cyclestar(nodes)
    #use (existing) regular graph with nodes-1 and degree-1
    else: # degree > 3 and degree * nodes % 2 == 1
        graph = networkx.random_regular_graph(degree - 1, nodes - 1, 0)
        #add missing node with full degree
        for i in range(0, degree - 1):
            graph.add_edge(i, nodes - 1)

    ########## GENERATE EDGES FILE ##########
    #verify feasibility of generated graph
    assert graph.number_of_nodes() == nodes
    assert graph.number_of_edges() <= math.floor((degree*nodes)/2)
    assert max([d for n, d in graph.degree()]) == degree
    assert networkx.is_connected(graph)
    basename = "n{}d{}.randomCS".format(nodes,degree)
    networkx.write_edgelist(graph, basename+".edges", data=False)
    return

########## FUNCTIONS ##########
def generate_cyclestar(nodes):
    starsize = math.floor(nodes / 2)
    cyclesize = nodes - starsize
    skipmax = math.floor(starsize / 2)
    assert cyclesize + starsize == nodes
    #creating basic cycle
    base = networkx.cycle_graph(cyclesize)
    #adding star connectors
    for star in range(0, 1):
        for i in range(starsize):
            base.add_edge(i, cyclesize + star * starsize + i)
    #prepare star-tries
    mindia = nodes
    skip = 2
    done = False
    #try stars
    while not done:
        graph = base.copy()
        i = 0
        j = -1
        #add star
        while j != 0:
            j = (skip+i)%starsize
            graph.add_edge(cyclesize+i,cyclesize+j)
            i = j
        #check result
        if networkx.is_connected(graph):
            assert max([d for n, d in graph.degree()]) == 3
            hops = networkx.shortest_path_length(graph, weight=None)
            diam, aspl = max_avg_for_matrix(hops)
            if diam < mindia or (diam == mindia and aspl < minaspl):
                mingraph = graph.copy()
                mindia = diam
                minaspl = aspl
        #prepare next star
        skip = skip + 1
        done = (skip > skipmax)
    return mingraph
    
def max_avg_for_matrix(data):
    cnt = 0
    sum = 0.0
    max = 0.0
    for i, row in data:
        for j, val in row.items():
            if i != j:
                cnt += 1
                sum += val
                if max < val:
                    max = val
    return max, sum / cnt

if __name__ == '__main__':
    main(argumentparser.parse_args())
