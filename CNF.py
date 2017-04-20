import sys
from copy import deepcopy


class CNF_converter:
    def __init__(self, filename):
        self.rules = {}
        self.non_terminals = set()
        self.terminals = set()
        self.start = None
        self.fresh_non_terminal_index = 0
        self.terminal_rule = {}
        self.__get_grammar(filename)

    def __get_grammar(self, filename):
        with open(filename) as file:
            lines = file.readlines()
            self.start = lines[0].strip()
            for line in lines[1:]:
                splitted = line.split("=")
                left = splitted[0].strip()
                self.rules[left] = []
                self.non_terminals.add(left)
                right = splitted[1].split("|")
                for rule in right:
                    split_concat = rule.strip().split("'")
                    self.rules[left].append([])
                    j = len(self.rules[left]) - 1
                    for i in range(len(split_concat)):
                        if i % 2 == 0:
                            self.non_terminals.update(split_concat[i].strip().split())
                            self.rules[left][j].extend(split_concat[i].strip().split())
                        else:
                            self.terminals.add(split_concat[i])
                            self.rules[left][j].append(split_concat[i])

            for non_terminal in self.rules.keys():
                if len(self.rules[non_terminal]) == 1 and len(self.rules[non_terminal][0]) == 1 \
                        and self.rules[non_terminal][0][0] in self.terminals:
                    self.terminal_rule[self.rules[non_terminal][0][0]] = non_terminal

    def print_grammar(self):
        for non_terminal in self.rules.keys():
            print(non_terminal, " = ", end=" ")
            for i, rule in enumerate(self.rules[non_terminal]):
                if len(rule) > 1:
                    for elem in rule:
                        elem = "'" + elem + "'" if elem in self.terminals else elem
                        print(elem, end=" ")
                else:
                    elem = "'" + rule[0] + "'" if rule[0] in self.terminals else rule[0]
                    print(elem, end="")
                if i != len(self.rules[non_terminal]) - 1:
                    print(" | ", end="")
            print()

    def __get_fresh_non_terminal_name(self):
        nterminal_name = "NEW"
        while nterminal_name in self.non_terminals:
            nterminal_name += str(self.fresh_non_terminal_index)
            self.fresh_non_terminal_index += 1
        self.non_terminals.add(nterminal_name)
        return nterminal_name

    def __remove_long_rules(self):
        for non_terminal in list(self.rules.keys()):
            for i in range(len(self.rules[non_terminal])):
                if len(self.rules[non_terminal][i]) > 2:
                    ruleset = self.rules[non_terminal][i]
                    self.rules[non_terminal].remove(self.rules[non_terminal][i])
                    new_terminal_count = len(ruleset) - 2

                    last_nterminal = non_terminal
                    for j in range(new_terminal_count):
                        new_nterminal_name = self.__get_fresh_non_terminal_name()
                        self.rules.setdefault(last_nterminal, [])
                        self.rules[last_nterminal].append([ruleset[j], new_nterminal_name])
                        last_nterminal = new_nterminal_name
                    self.rules.setdefault(last_nterminal, [])
                    self.rules[last_nterminal].append([ruleset[new_terminal_count], ruleset[new_terminal_count + 1]])

    def __get_eps_generating_set(self):
        eps_set = set()
        for non_terminal in self.rules.keys():
            if non_terminal != self.start:
                for rule in self.rules[non_terminal]:
                    if 'eps' in rule and len(rule) == 1:
                        eps_set.add(non_terminal)
                        break

        old_eps_set = set()
        while len(eps_set - old_eps_set) != 0:
            old_eps_set = deepcopy(eps_set)
            for non_terminal in self.rules.keys():
                for rule in self.rules[non_terminal]:
                    if set(rule).issubset(eps_set):
                        eps_set.add(non_terminal)
                        continue
        return eps_set

    def __remove_eps_rules(self):
        eps_set = self.__get_eps_generating_set()

        for non_terminal in self.rules.keys():
            for rule in self.rules[non_terminal]:
                if len(eps_set.intersection(set(rule))) != 0:  # rule contains eps-generating
                    # non terminals
                    if rule[0] in eps_set:
                        # EPS ANOTHER case
                        if len(rule) > 1 and [rule[1]] not in self.rules[non_terminal]:
                            self.rules[non_terminal].append([rule[1]])
                    if len(rule) > 1:
                        # ANOTHER EPS case
                        if rule[1] in eps_set and [rule[0]] not in self.rules[non_terminal]:
                            self.rules[non_terminal].append([rule[0]])
        for non_terminal in list(self.rules.keys()):
            for rule in self.rules[non_terminal]:
                if 'eps' in rule and len(rule) == 1 and non_terminal != self.start:
                    self.rules[non_terminal].remove(rule)

    def __remove_chain_rules(self):
        chain_rule_found = True
        while chain_rule_found:
            chain_rule_found = False
            for non_terminal in self.rules.keys():
                for rule in self.rules[non_terminal]:
                    # it is a chain rule
                    if len(rule) == 1 and rule[0] in self.non_terminals:
                        chain_rule_found = True
                        self.rules[non_terminal].remove(rule)
                        for chained_rule in self.rules[rule[0]]:
                            if chained_rule not in self.rules[non_terminal]:
                                self.rules[non_terminal].append(chained_rule)

    def __remove_non_generating_nonterminals(self):
        generating = set()

        for non_terminal in self.rules.keys():
            for rule in self.rules[non_terminal]:
                if set(rule).issubset(self.terminals):
                    generating.add(non_terminal)

        old_gen_set = set()
        while len(generating - old_gen_set) != 0:
            old_gen_set = deepcopy(generating)
            for non_terminal in self.rules.keys():
                for rule in self.rules[non_terminal]:
                    if set(rule).intersection(self.non_terminals).issubset(generating):
                        generating.add(non_terminal)

        for non_terminal in list(self.rules.keys()):
            all_rights = set([item for sublist in self.rules[non_terminal] for item in sublist])
            all_rights = all_rights.intersection(self.non_terminals)
            if not all_rights.issubset(generating):
                del self.rules[non_terminal]

    def __remove_non_reachable_nonterminals(self):
        reachable = set()
        reachable.add(self.start)

        old_reachable = set()
        while len(reachable - old_reachable) != 0:
            old_reachable = deepcopy(reachable)
            for non_terminal in self.rules.keys():
                if non_terminal in reachable:
                    all_rights = set([item for sublist in self.rules[non_terminal] for item in sublist])
                    all_rights = all_rights.intersection(self.non_terminals)
                    reachable.update(all_rights)

        for non_terminal in list(self.rules.keys()):
            if non_terminal not in reachable:
                del self.rules[non_terminal]
                self.non_terminals.remove(non_terminal)

    def __remove_useless_rules(self):
        self.__remove_non_generating_nonterminals()
        self.__remove_non_reachable_nonterminals()

    def __remove_term_pairs(self):
        for non_terminal in list(self.rules.keys()):
            for rule in self.rules[non_terminal]:
                if len(rule) == 2 and (rule[0] in self.terminals or rule[1] in self.terminals):
                    if rule[0] in self.terminals:
                        if self.terminal_rule.get(rule[0], None) is None:
                            new_non_term = self.__get_fresh_non_terminal_name()
                            self.rules[new_non_term] = [[rule[0]]]
                            self.terminal_rule[rule[0]] = new_non_term
                            rule[0] = new_non_term
                        else:
                            rule[0] = self.terminal_rule[rule[0]]
                    if rule[1] in self.terminals:
                        if self.terminal_rule.get(rule[1], None) is None:
                            new_non_term = self.__get_fresh_non_terminal_name()
                            self.rules[new_non_term] = [[rule[1]]]
                            self.terminal_rule[rule[0]] = new_non_term
                            rule[1] = new_non_term
                        else:
                            rule[1] = self.terminal_rule[rule[1]]

    def get_cnf(self):
        old_start = self.start
        if ['eps'] in self.rules[old_start]:
            self.start = self.__get_fresh_non_terminal_name()
            self.rules[self.start] = [[old_start]]
            self.rules[self.start].append(['eps'])

        self.__remove_long_rules()
        self.__remove_eps_rules()
        self.__remove_chain_rules()
        self.__remove_useless_rules()
        self.__remove_term_pairs()
        return self


if __name__ == '__main__':
    filename = sys.argv[1]
    cnf = CNF_converter(filename)
    cnf.get_cnf()
    cnf.print_grammar()
