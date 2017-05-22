import sys
import csv
from CNF import CNF_converter
import pydot


class ParseTreeNode:
    graph = pydot.Dot(graph_type='digraph')
    i = 0

    def __init__(self, left, right, non_terminal, word):
        self.left = left
        self.right = right
        self.nt = non_terminal
        self.word = word
        self.step = None

    def __str__(self):
        if self.step is None:
            self.step = ParseTreeNode.i
            ParseTreeNode.i += 1
        return self.nt + "\n" + str(self.step) + ". " + self.word

    def create_graph(self):
        if self.left is not None:
            edge = pydot.Edge(self.__str__(), self.left.__str__())
            ParseTreeNode.graph.add_edge(edge)
            self.left.create_graph()
        if self.right is not None:
            edge = pydot.Edge(self.__str__(), self.right.__str__())
            ParseTreeNode.graph.add_edge(edge)
            self.right.create_graph()


def write_to_csv(table, filename):
    with open(filename + '.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(table)


def CYK(grammar, sequence):
    cnf = CNF_converter(grammar).get_cnf()
    # cnf.print_grammar()
    non_terminals = list(cnf.non_terminals)
    index = {k: v for v, k in enumerate(non_terminals)}
    with open(sequence) as file:
        seq = file.read().rstrip()
    n = len(seq)
    dtable = [[[None for _ in range(len(non_terminals))] for _ in range(n)] for _ in range(n)]
    csv_dtable = [[[] for _ in range(n)] for _ in range(n)]

    for i, symbol in enumerate(seq):
        for a, non_terminal in enumerate(non_terminals):
            if [symbol] in cnf.rules[non_terminal]:
                dtable[i][i][a] = ParseTreeNode(None, None, non_terminals[a], symbol)
                csv_dtable[i][i].append(non_terminals[a])

    for length in range(1, n):
        for i in range(n - length):
            j = i + length
            for k in range(i, j):
                for A in cnf.rules.keys():
                    for rule in cnf.rules[A]:
                        if len(rule) == 2:
                            left = dtable[i][k][index[rule[0]]]
                            right = dtable[k + 1][j][index[rule[1]]]
                            if left and right:
                                dtable[i][j][index[A]] = ParseTreeNode(None, None, A, left.word + right.word)
                                dtable[i][j][index[A]].left = dtable[i][k][index[rule[0]]]
                                dtable[i][j][index[A]].right = dtable[k + 1][j][index[rule[1]]]

                                csv_dtable[i][j].append(A)

    write_to_csv(csv_dtable, grammar)
    root = dtable[0][n - 1][index[cnf.start]]
    if root is not None:
        print(True)
        root.create_graph()
        ParseTreeNode.graph.write_png(grammar + ".png")
    else:
        print(False)


def main():
    grammar = sys.argv[1]
    sequence = sys.argv[2]
    CYK(grammar, sequence)


main()
