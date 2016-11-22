"""
This module contains the lexer.

--- DO NOT MODIFY THIS FILE ---
"""

import re

from symbols import *

# regular expressions defining the tokens:
token_regex = dict()
token_regex[LB] = '\\{'
token_regex[RB] = '\\}'
token_regex[LS] = '\\['
token_regex[RS] = '\\]'
token_regex[COMMA] = ','
token_regex[COLON] = ':'
token_regex[INT] = '\d+'
token_regex[STRING] = '"[^"]*"'

def lex(text):
    """
    Parse the string given by text, and return a list of the form:
    [(terminal, value), (terminal, value), ...]
    """
    whitespace = '[ \\n\\t]+'
    tokens = []
    pos = 0
    while pos < len(text):
        m = re.match(whitespace, text[pos:])
        if not m:
            for token, pattern in token_regex.items():
                m = re.match(pattern, text[pos:])
                if m:
                    tokens.append((token, m.group(0)))
                    break
        if m:
            pos += m.end(0)
        else:
            raise Exception("Bad token at: {}".format(pos))
    return tokens


if __name__ == '__main__':
    json_example = open('json_example.json').read()
    print json_example
    print
    tokens = lex(json_example)
    print "tokens:"
    for t in tokens:
        print "  ", t
