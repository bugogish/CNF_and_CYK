import sys
import pydot
from copy import deepcopy

from CNF import CNF_converter


def read_graph(graph_fname):
    with open(graph_fname) as file:
        n = int(file.readline())
        graph = [{} for _ in range(n)]
        for line in file:
            edge = line.split()
            graph[int(edge[0])][int(edge[1])] = edge[2]
    return graph


def SGA(graph_source, grammar_source, from_file=True):
    grammar = CNF_converter(grammar_source).get_cnf()
    # grammar.print_grammar()
    non_terminals = list(grammar.non_terminals)
    index = {k: v for v, k in enumerate(non_terminals)}

    if from_file:
        graph = read_graph(graph_source)
    else:
        graph = graph_source

    dtable = [[[False for _ in range(len(non_terminals))] for _ in range(len(graph))] for _ in range(len(graph))]
    n = len(graph)

    for v1 in range(n):
        for v2 in graph[v1].keys():
            for a, non_terminal in enumerate(non_terminals):
                if [graph[v1][v2]] in grammar.rules[non_terminal]:
                    dtable[v1][v2][a] = True
                if ['eps'] in grammar.rules[non_terminal]:
                    dtable[v1][v1][a] = True
                    dtable[v2][v2][a] = True

    flag = True

    while flag:
        flag = False
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    for A in grammar.rules.keys():
                        for rule in grammar.rules[A]:
                            if len(rule) == 2:
                                left = dtable[i][k][index[rule[0]]]
                                right = dtable[k][j][index[rule[1]]]
                                if left and right:
                                    if not dtable[i][j][index[A]]:
                                        flag = True
                                    dtable[i][j][index[A]] = True

    return dtable, grammar, index


def main():
    grammar = sys.argv[1]
    graph = sys.argv[2]
    dtable, grammar, index = SGA(graph, grammar)
    n = len(dtable)
    for i in range(n):
        for j in range(n):
            for k in range(len(grammar.non_terminals)):
                if dtable[i][j][k]:
                    print("({}, {}, {})".format(i, j, grammar.non_terminals[k]))


if __name__ == '__main__':
    main()
