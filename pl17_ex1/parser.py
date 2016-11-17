"""
This file contains the JSON parser.
"""

from symbols import *


class SyntaxError(Exception):
    pass


class Parser(object):
    """
    Class with basic functionality for parsers.

    --- DO NOT MODIFY THIS CLASS ---
    """
    def __init__(self, tokens):
        """
        Initialize the parser.
        tokens is a list of pairs of the form:
        [(t1, v1), (t2, v2), ...]
        where ti's are in terminals, and vi's are values attached to them.
        The list is in the format returned by the lexer.

        --- DO NOT MODIFY THIS FUNCTION ---
        """
        self.tokens = tokens
        self.pos = -1
        self.advance() # updates self.t, which keeps the current terminal

    def advance(self):
        """
        Return the value attached to current token, and advance by one.
        Return EOF once all tokens are exhausted.

        --- DO NOT MODIFY THIS FUNCTION ---
        """
        if self.pos < len(self.tokens):
            value = self.tokens[self.pos][1]
        else:
            value = EOF
        self.pos += 1
        if self.pos < len(self.tokens):
            self.t = self.tokens[self.pos][0]
        else:
            self.t = EOF
        return value

    def match(self, terminal):
        """
        Match the next token against the given terminal. Raise a
        SyntaxError if they do not match.
        If they do, return the value attached to the current token.

        --- DO NOT MODIFY THIS FUNCTION ---
        """
        if self.t == terminal:
            value = self.advance()
            print "matched {:10} {}".format(terminal, value)
            return value
        else:
            raise SyntaxError("Syntax error: expected {}, found {}".format(
                terminal, self.t))


class JsonParser(Parser):
    """
    A JSON parser.

    --- COMPLETE THIS CLASS IN QUESTION 6 ---
    """
    def parse(self):
        """
        Parse the input by parsing the start symbol (obj) and then matching EOF.

        --- DO NOT MODIFY THIS FUNCTION ---
        """
        result = self.parse_obj()
        self.match(EOF)
        return result

    def parse_keyvalue(self):
        """
        An example parse_<nonterminal> function.

        --- DO NOT MODIFY THIS FUNCTION ---
        """
        if self.t in [STRING]:
            c1 = self.match(STRING)
            c2 = self.match(COLON)
            c3 = self.parse_value()
            return (keyvalue, (c1, c2, c3))
        else:
            raise SyntaxError("Syntax error: no rule for token: {}".format(self.t))

    def parse_obj(self):
        #
        # --- CHANGE THE BODY OF THIS FUNCTION ---
        #
        """
        Parses the obj non-terminal according to its production rule and its select set:
        obj -> LB E RB  (select set: {LB})
        """
        if self.t == LB:
            c1 = self.match(LB)
            c2 = self.parse_E()
            c3 = self.match(RB)
            return (obj, (c1, c2, c3))
        else:
            raise SyntaxError("Syntax error: no rule for token: {}".format(self.t))
        
    #
    # --- FILL IN MORE parse_XXX FUNCTIONS HERE ---
    #

    def parse_E(self):
        """
        Parses the E non-terminal according to its production rules and their select sets:
        E -> members (select set: {STRING})
        E -> epsilon (select set: {RB})
        """
        if self.t == STRING:
            # Applying the rule E -> members
            c1 = self.parse_members()
            return (E, (c1,))
        elif self.t == RB:
            # Applying the rule E -> epsilon
            return (E, ())
        else:
            raise SyntaxError("Syntax error: no rule for token: {}".format(self.t))
        
    def parse_members(self):
        """
        Parses the members non-terminal according to its production rule and its select set:
        members -> keyvalue MembersTag  (select set: {STRING})
        """
        if self.t == STRING:
            # Applying the rule members -> keyvalue MembersTag
            c1 = self.parse_keyvalue()
            c2 = self.parse_MembersTag()
            return (members, (c1, c2))
        else:
            raise SyntaxError("Syntax error: no rule for token: {}".format(self.t))

    def parse_MembersTag(self):
        """
        Parses the MembersTag non-terminal according to its production rules and their select sets:
        MembersTag -> COMMA keyvalue MembersTag (select set: {COMMA})
        MembersTag -> epsilon                   (select set: {RB})
        """
        if self.t == COMMA:
            # Applying the rule MembersTag -> COMMA keyvalue MembersTag
            c1 = self.match(COMMA)
            c2 = self.parse_keyvalue()
            c3 = self.parse_MembersTag()
            return (MembersTag, (c1, c2, c3))
        elif self.t == RB:
            # Applying the rule MembersTag -> epsilon
            return (MembersTag, ())
        else:
            raise SyntaxError("Syntax error: no rule for token: {}".format(self.t))
        
    def parse_value(self):
        """
        Parses the value non-terminal according to its production rules and their select sets:
        value -> STRING (select set: {STRING})
        value -> INT (select set: {INT})
        value -> obj (select set: {LB})
        """
        if self.t == STRING:
            # Applying the rule value -> STRING
            c1 = self.match(STRING)
            return (value, (c1,))
        elif self.t == INT:
            # Applying the rule value -> INT
            c1 = self.match(INT)
            return (value, (c1,))
        elif self.t == LB:
            # Applying the rule value -> obj
            c1 = self.parse_obj()
            return (value, (c1,))
        else:
            raise SyntaxError("Syntax error: no rule for token: {}".format(self.t))

def create_tree(input_file_name, output_file_name):
    from lexer import lex
    from tree_to_dot import tree_to_dot, view
    
    json_example = open(input_file_name).read()
    print json_example
    tokens = lex(json_example)
    parser = JsonParser(tokens)
    parse_tree = parser.parse()
    dot = tree_to_dot(parse_tree)
    open(output_file_name, 'w').write(dot)
            
def main():
    from lexer import lex
    from tree_to_dot import tree_to_dot, view

    json_example = open('json_example.json').read()
    print json_example
    tokens = lex(json_example)
    parser = JsonParser(tokens)
    parse_tree = parser.parse()
    dot = tree_to_dot(parse_tree)
    open('json_example.gv', 'w').write(dot)
    view(dot)

    #
    # --- MODIFY HERE TO ADD MORE TEST CASES ---
    #
    
    # Uncomment the following line in order to check the syntax exception.
    # create_tree('json_bad_example.json', 'json_bad_example.gv')

if __name__ == '__main__':
    main()
