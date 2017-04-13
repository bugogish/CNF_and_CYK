import sys
import csv
from CNF import CNF_converter


def write_to_csv(table, filename):
    with open(filename + '.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(table)


def CYK(grammar, sequence):
    cnf = CNF_converter(grammar).get_cnf()
    non_terminals = list(cnf.non_terminals)
    index = {k: v for v, k in enumerate(non_terminals)}
    with open(sequence) as file:
        seq = file.read()
    n = len(seq)
    dtable = [[[False for _ in range(len(non_terminals))] for _ in range(n)] for _ in range(n)]
    out_dtable = [[[] for _ in range(n)] for _ in range(n)]

    for i, symbol in enumerate(seq):
        for a, non_terminal in enumerate(non_terminals):
            if [symbol] in cnf.rules[non_terminal]:
                dtable[i][i][a] = True
                out_dtable[i][i].append(non_terminals[a])
    for length in range(1, n):
        for i in range(n - length):
            j = i + length
            for k in range(i, j):
                for A in cnf.rules.keys():
                    for rule in cnf.rules[A]:
                        if len(rule) == 2:
                            if dtable[i][k][index[rule[0]]] and dtable[k + 1][j][index[rule[1]]]:
                                dtable[i][j][index[A]] = True
                                out_dtable[i][j].append(A)

    write_to_csv(out_dtable, grammar)

    print(dtable[0][n - 1][index[cnf.start]])


def main():
    grammar = sys.argv[1]
    sequence = sys.argv[2]
    CYK(grammar, sequence)


main()
