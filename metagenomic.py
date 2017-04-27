from random import randint, choice

import pydot

from SGA import SGA

MIN_NUM_EDGES = 1000
MAX_NUM_EDGES = 1500
MIN_N_VERTICES = 100
MAX_N_VERTICES = 150
sigma = 'acgt'
grammar_path = "tRNA"


def get_label():
    return choice(sigma)


def generate_assembly():
    # visual_graph = pydot.Dot(graph_type='digraph')
    visual_graph = None
    n_edges = randint(MIN_NUM_EDGES, MAX_NUM_EDGES)
    n_vertices = randint(MAX_N_VERTICES, MAX_N_VERTICES)
    graph = [{} for _ in range(n_vertices)]
    edges = set()
    while len(edges) != n_edges:
        v1 = randint(0, n_vertices - 1)
        v2 = randint(0, n_vertices - 1)
        if v1 != v2 and (v1, v2) not in edges:
            graph[v1][v2] = get_label()
            edges.add((v1, v2))
            # edge = pydot.Edge(v1, v2, label=graph[v1][v2])
            # visual_graph.add_edge(edge)
    return graph, visual_graph


def main():
    graph, visual_graph = generate_assembly()
    # visual_graph.write_png("metagenomic" + ".png")
    dtable, grammar, index = SGA(graph, grammar_path, from_file=False)
    non_terminals = list(grammar.non_terminals)
    n = len(graph)
    for i in range(n):
        for j in range(n):
            if dtable[i][j][index[grammar.start]]:
                print("({}, {}, {})".format(i, j, non_terminals[index[grammar.start]]))


main()
