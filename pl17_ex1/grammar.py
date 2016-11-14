"""
This module contains functions for analyzing a grammar, finding
its NULLABLE, FIRST, FOLLOW and SELECT sets, and determining if it is
LL(1).

A grammar is represented as a list of rules of the form (head, body)
where head is the goal non-terminal, and body is a tuple of symbols,
or the empty tuple () for an epsilon rule.

The start symbol is always the head of the first rule in the list.
"""

from symbols import *


grammar_recitation = [
    (S, (ID, ASSIGN, E)),              # S -> id := E
    (S, (IF, LP, E, RP, S, ELSE, S)),  # S -> if (E) S else S
    (E, (T, EP)),                      # E -> T EP
    (T, (ID,)),                        # T -> id
    (T, (LP, E, RP)),                  # T -> (E)
    (EP, ()),                          # EP -> epsilon
    (EP, (PLUS, E)),                   # EP -> + E
]


def calculate_nullable(terminals, nonterminals, grammar):
    """
    Return the set of nullable nonterminals in the given grammar.

    terminals and nonterminals are sets, grammer is a list of rules as
    explained above.

    --- DO NOT MODIFY THIS FUNCTION ---
    """
    nullable = set()
    for head, body in grammar:
        if body == ():
            nullable.add(head)
    changing = True
    while changing:
        changing = False
        for head, body in grammar:
            if set(body) <= nullable and head not in nullable:
                nullable.add(head)
                changing = True
    return nullable


def calculate_first(terminals, nonterminals, grammar, nullable):
    """
    Return a dictionary mapping terminals and nonterminals to their FIRST set
    """
    first = dict()
    for t in terminals:
        first[t] = {t}
    for a in nonterminals:
        first[a] = set()
    changing = True
    while changing:
        changing = False
        for head, body in grammar:
            for symbol in body:
                # if the current symbol is a terminal - no need for further check,
                #                                   just add the terminal to head's first-set (if not exist)
                if symbol in terminals:
                    if not symbol in first[head]:
                        first[head].add(symbol)
                        changing = True
                    break

                if symbol in nonterminals:
                    # add current nonTerminal's first-set to head's first-set (if not exist)
                    for terminal in first[symbol]:
                        if not (terminal in first[head]):
                            first[head].add(terminal)
                            changing = True

                    # if the nonTerminal is not nullable there is no need to
                    # continue the check for possible firsts in current rule
                    if not (symbol in nullable):
                        break

                # unknown symbol in the grammar
                else:
                    print("Error! unknown symbol: " + str(symbol))
                    # brutal exist
                    exit(0)

    return first


def calculate_follow(terminals, nonterminals, grammar, nullable, first):
    """
    Return a dictionary mapping terminals and nonterminals to their FOLLOW set
    """
    follow = dict()
    for a in nonterminals:
        follow[a] = set()
    start_nonterminal = grammar[0][0]
    follow[start_nonterminal] = {EOF}

    changing = True
    while changing:
        changing = False
        for head, body in grammar:
            # First Phase: For each rule we iterate on the symbols from left to right (last to first)
            #             until we'll reach a non nullable symbol (terminal or non nullable nonTerminal)
            #             On each iteration we will add Follow(symbol) to the Follow of the current Rule-NonTerminal
            for bodyIndex in range(len(body), 0, -1):
                symbol = body[bodyIndex - 1] # -1 to convert from position to index

                # if the current symbol is a terminal - no need for further check
                if symbol in terminals:
                    break

                if symbol in nonterminals:
                    # add Follow(head) to symbol's follow-set (if not exist)
                    for terminal in follow[head]:
                        if not (terminal in follow[symbol]):
                            follow[symbol].add(terminal)
                            changing = True

                    # if the nonTerminal is not nullable there is no need to
                    # continue the check for possible followers in current rule
                    if not (symbol in nullable):
                        break

                # unknown symbol in the grammar
                else:
                    print("Error! unknown symbol: " + str(symbol))
                    # brutal exist
                    exit(0)

            # Second Phase: For each nonTerminal "T" in the rule we need to check 2 things:
            #                   1) if there are nullable nonTerminals after it -
            #                       in order to add Follow(T) the First-set of the nullable nonTerminals.
            #                   2) if there is a terminal - and add it to Follow(T)
            bodyIndex = 0
            while (bodyIndex < len(body)-1):
                symbolIndex = bodyIndex
                symbol = body[symbolIndex] # current symbol

                # the logic in only relevnt for nonTerminals
                if symbol in terminals:
                    bodyIndex += 1
                    continue
                elif not (symbol in nonterminals):
                    print("Error! unknown symbol: " + str(symbol))
                    # brutal exist
                    exit(0)

                # at this point symbol must be nonTerminal

                while (bodyIndex < len(body)):
                    bodyIndex = bodyIndex + 1
                    nextSymbol = body[bodyIndex] # next symbol

                    # if the current symbol is a terminal - no need for further check,
                    #          just add the terminal to all the followers from symbol to nextSymbol(not included nextSymbol)
                    if nextSymbol in terminals:
                        for index in range(symbolIndex, bodyIndex, 1):
                            updateSymbol = body[index]
                            if not (nextSymbol in follow[updateSymbol]):
                                follow[updateSymbol].add(nextSymbol)
                                changing = True

                        # update bodyIndex, since a terminal has no followers
                        bodyIndex += 1
                        break


                    if nextSymbol in nonterminals:
                        # add First(nextSymbol) to all the followers from symbol to nextSymbol (not included nextSymbol)
                        for index in range(symbolIndex, bodyIndex, 1):
                            updateSymbol = body[index]
                            for terminal in first[nextSymbol]:
                                if not (terminal in follow[updateSymbol]):
                                    follow[updateSymbol].add(terminal)
                                    changing = True

                        # if nextSymbol is not nullable there is no need to
                        # continue the check for possible followers to symbol
                        if not (nextSymbol in nullable):
                            # no need to update bodyIndex since we want to find possible followers for nextSymbol
                            break

                    # unknown symbol in the grammar
                    else:
                        print("Error! unknown symbol: " + str(nextSymbol))
                        # brutal exist
                        exit(0)

                    # update bodyIndex to search for longer nullable sequence
                    bodyIndex += 1

    return follow


def calculate_select(terminals, nonterminals, grammar, nullable, first, follow):
    """
    Return a dictionary mapping rules to their SELECT (a.k.a. PREDICT) set
    """
    select = dict()

    #consts
    HEAD_RULE_INDEX = 0
    BODY_RULE_INDEX = 1

    for ruleIndex in range(len(grammar)):
        # each rule as a key in select dict
        ruleKey = grammar[ruleIndex]

        head = grammar[ruleIndex][HEAD_RULE_INDEX]
        body = grammar[ruleIndex][BODY_RULE_INDEX]

        isBodyNullable = True
        # check whether the body is nullable ( = is it possible to apply certain rules
        # to the body's nonTerminals such that the result would be a null)
        for symbol in body:
            if (symbol in terminals) or not (symbol in nullable):
                isBodyNullable = False
                break


        # create First(body) (= all the possible firsts terminals for the current rule)
        bodyFirst = set()
        for symbol in body:
            # if symbol is a terminal stop iteration
            if symbol in terminals:
                bodyFirst.add(symbol)
                break

            if symbol in nonterminals:
                # add First(symbol) to bodyFirst
                bodyFirst = bodyFirst | first[symbol]

                # if symbol is not nullable there is no need to
                # continue the check for possible firsts
                if not (symbol in nullable):
                    break
            else:
                print("Error! unknown symbol: " + str(symbol))
                # brutal exist
                exit(0)


        select[ruleKey] = bodyFirst

        if isBodyNullable:
            select[ruleKey] = select[ruleKey] | follow[head]

    return select


def format_rule(r):
    """
    --- DO NOT MODIFY THIS FUNCTION ---
    """
    return "{} -> {}".format(r[0], ' '.join(r[1]))


def find_terminals_and_nonterminals(grammar):
    """
    Find the terminals and nonterminals appearing in the given grammar.

    --- DO NOT MODIFY THIS FUNCTION ---
    """
    symbols = set()
    nonterminals = set()
    for head, body in grammar:
        nonterminals.add(head)
        symbols.update(body)
    terminals = symbols - nonterminals
    return terminals, nonterminals


def analyze_grammar(grammar):
    """
    Use other functions in this module to analyze the grammar and
    check if it is LL(1).

    --- DO NOT MODIFY THIS FUNCTION ---
    """
    print "Analyzing grammar:"
    for r in grammar:
        print "    " + format_rule(r)
    print

    terminals, nonterminals = find_terminals_and_nonterminals(grammar)
    print "terminals = ", terminals
    print "nonterminals = ", nonterminals
    print

    nullable = calculate_nullable(terminals, nonterminals, grammar)
    print "nullable = ", nullable
    print

    first = calculate_first(terminals, nonterminals, grammar, nullable)
    for k in sorted(first.keys()):
        print "first({}) = {}".format(k, first[k])
    print

    follow = calculate_follow(terminals, nonterminals, grammar, nullable, first)
    for k in sorted(follow.keys()):
        print "follow({}) = {}".format(k, follow[k])
    print

    select = calculate_select(terminals, nonterminals, grammar, nullable, first, follow)
    for k in sorted(select.keys()):
        print "select({}) = {}".format(format_rule(k), select[k])
    print

    ll1 = True
    n = len(grammar)
    for i in range(n):
        for j in range(i+1, n):
            r1 = grammar[i]
            r2 = grammar[j]
            if r1[0] == r2[0] and len(select[r1] & select[r2]) > 0:
                ll1 = False
                print "Grammar is not LL(1), as the following rules have intersecting SELECT sets:"
                print "    " + format_rule(r1)
                print "    " + format_rule(r2)
    if ll1:
        print "Grammar is LL(1)."
    print


grammar_json_4a = [
    (obj, (LB,RB)),              # obj -> {}
    (obj, (LB,members,RB)),  # obj -> {members}
    (members, (keyvalue,)),                      # members -> keyvalue
    (members, (members,COMMA,members)),                        # members -> members, members
    (keyvalue, (STRING,COLON,value)),                  # keyvalue -> string : value
    (value, (STRING,)),                          # value -> string
    (value, (INT,)),                   # value -> int
     (value, (obj,)),                     # value -> obj
]

grammar_json_4b = [
    (obj, (LB,RB)),          # obj -> {}
    (obj, (LB,members,RB)),  # obj -> {members}
    (members, (keyvalue,)),                            # members -> keyvalue
    (members, (members,COMMA,keyvalue)),               # members -> members, keyvalue
    (keyvalue, (STRING,COLON,value)),                  # keyvalue -> string : value
    (value, (STRING,)),                          # value -> string
    (value, (INT,)),                   # value -> int
     (value, (obj,)),                     # value -> obj

]

grammar_json_4c = [
    (obj, (LB,E,RB)),           # obj -> {E}
    (E, (members,)),             # E -> members
    (E, ()),                    # E -> epsilon
    (members, (keyvalue,MembersTag)),                      # members -> keyvalueMembersTag
    (MembersTag, (COMMA,keyvalue,MembersTag)),             # MembersTag -> , keyvalueMembersTag
    (MembersTag, ()),                                      # MembersTag -> epsilon
    (keyvalue, (STRING,COLON,value)),                  # keyvalue -> string : value
    (value, (STRING,)),                          # value -> string
    (value, (INT,)),                   # value -> int
     (value, (obj,)),                     # value -> obj

]

grammar_json__6 = [
    #
    # --- FILL IN HERE IN QUESTION 7 ---
    #
]



def main():
    analyze_grammar(grammar_recitation)
    print

    #
    # --- UNCOMMENT THE FOLLOWING LINES AS YOU PROCEED ---
    #
    analyze_grammar(grammar_json_4a)
    print
    analyze_grammar(grammar_json_4b)
    print
    analyze_grammar(grammar_json_4c)
    print
    # analyze_grammar(grammar_json_6)
    # print

    #
    # --- ADD MORE TEST CASES HERE ---
    #


if __name__ == '__main__':
    main()
