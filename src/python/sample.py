
"""
Lexical analyzer.

Generated from 'sample.lang' by LANG.
"""


# -------------------
# Constants start
# -------------------

COMMENT = 5

IF = "if"

NUMBER = 2

OPERATOR = 3

STRING = 4

THEN = "then"

WS = 1

# -------------------
# Constants end
# -------------------


# -------------------
# Definitions start
# -------------------


class LangException(Exception):
    def __init__(self, line, message):
        self.line = line
        self.msg  = message

    def __str__(self):
        return self.msg + ":\n" + self.line

class PyLexer(object):
    def __init__(self, input):
        self.input        = input
        self.input_index  = 0
        self.lexeme_begin = 0
        self.start_state  = 0
        self.curr_state   = 0
        self._yystart     = 0
        self._yyend       = 0
        self._yytoken     = None
        self._yyid        = None
        self._yynum       = None

        self.table = []
        self.install_transitions()

        self._rules = {}
        self.install_rules()

        self.user_variables = {}

    def put_table(self, state, fn, next_start=None):
        if state >= len(self.table):
            for i in range(len(self.table), state+8):
                self.table.append(None)
        self.table[state] = [fn, next_start]

    def raise_exception(self):
        start  = max(self.input_index - 20, 0)
        data   = self.input[start:self.input_index+1]
        start  = max(start, data.rfind("\n"))
        length = min(self.input_index, len(self.input)) + 1 - start
        data   = data + "\n" + ("-" * (length-1)) + "^"
        raise LangException(data, "Failed to parse input")

    def nextchar(self):
        if self.input_index > len(self.input):
            self.raise_exception()
        i = self.input_index
        self.input_index += 1
        if i < len(self.input):
            return self.input[i]
        return None

    def eof(self):
        return self.input_index >= len(self.input)

    def retract(self, n=1):
        self.input_index -= n
        if self.input_index < 0:
            self.input_index = 0

    def get_transition(self, state):
        return self.table[state][0]

    def get_next_state(self, state):
        return self.table[state][1]
            
    def nexttoken(self):
        while True:
            # Nothing matched
            if self.curr_state is None:
                if self.eof(): return None
                self.raise_exception()

            fn = self.get_transition(self.curr_state)
            # Unknown transition
            if fn is None:
                if self.eof(): return None
                self.raise_exception()

            retval = fn(self)
            if retval is not None:
                return retval

    def yystart(self):
        return self._yystart

    def yyend(self):
        return self._yyend

    def yytoken(self):
        return self._yytoken

    def matched(self, definition):
        self.curr_state  = 0
        self.start_state = 0

        self._yystart = self.lexeme_begin
        self._yyend   = self.input_index
        self._yytoken = self.input[self._yystart:self._yyend]

        self.lexeme_begin = self.input_index

        rule = self._rules.get(definition)
        if not rule:
            rule = self._rules.get(self._yytoken)
        if rule:
            return rule(self)
        return

    def fail(self):
        self.input_index = self.lexeme_begin
        self.start_state = self.get_next_state(self.start_state)
        return self.start_state

    def match_1(self):

        
        return self.matched(WS)

    def match_0(self):

        c = self.nextchar()

        if c == ' ':
            self.curr_state = 1
            return

        if c == 'n':
            self.curr_state = 1
            return

        if c == 'r':
            self.curr_state = 1
            return

        if c == 't':
            self.curr_state = 1
            return

        self.retract()
        self.curr_state = self.fail()

    def match_3(self):

        c = self.nextchar()

        if c == '0':
            self.curr_state = 3
            return

        if c == '1':
            self.curr_state = 3
            return

        if c == '2':
            self.curr_state = 3
            return

        if c == '3':
            self.curr_state = 3
            return

        if c == '4':
            self.curr_state = 3
            return

        if c == '5':
            self.curr_state = 3
            return

        if c == '6':
            self.curr_state = 3
            return

        if c == '7':
            self.curr_state = 3
            return

        if c == '8':
            self.curr_state = 3
            return

        if c == '9':
            self.curr_state = 3
            return

        self.retract()
        return self.matched(NUMBER)

    def match_2(self):

        c = self.nextchar()

        if c == '0':
            self.curr_state = 3
            return

        if c == '1':
            self.curr_state = 3
            return

        if c == '2':
            self.curr_state = 3
            return

        if c == '3':
            self.curr_state = 3
            return

        if c == '4':
            self.curr_state = 3
            return

        if c == '5':
            self.curr_state = 3
            return

        if c == '6':
            self.curr_state = 3
            return

        if c == '7':
            self.curr_state = 3
            return

        if c == '8':
            self.curr_state = 3
            return

        if c == '9':
            self.curr_state = 3
            return

        self.retract()
        self.curr_state = self.fail()

    def match_5(self):

        
        return self.matched(OPERATOR)

    def match_4(self):

        c = self.nextchar()

        if c == '*':
            self.curr_state = 5
            return

        if c == '+':
            self.curr_state = 5
            return

        if c == '-':
            self.curr_state = 5
            return

        if c == '/':
            self.curr_state = 5
            return

        self.retract()
        self.curr_state = self.fail()

    def match_7(self):

        
        return self.matched(STRING)

    def match_6(self):

        c = self.nextchar()

        if c == '"':
            self.curr_state = 8
            return

        self.retract()
        self.curr_state = self.fail()

    def match_8(self):

        c = self.nextchar()

        self.curr_state = 9
        return

    def match_9(self):

        c = self.nextchar()

        if c == '"':
            self.curr_state = 7
            return

        self.curr_state = 9
        return

    def match_11(self):

        
        return self.matched(COMMENT)

    def match_10(self):

        c = self.nextchar()

        if c == '#':
            self.curr_state = 12
            return

        self.retract()
        self.curr_state = self.fail()

    def match_12(self):

        c = self.nextchar()

        self.curr_state = 13
        return

    def match_13(self):

        c = self.nextchar()

        if c == 'n':
            self.curr_state = 11
            return

        self.curr_state = 13
        return

    def install_transitions(self):

        self.put_table(0, PyLexer.match_0, 2)

        self.put_table(1, PyLexer.match_1, None)

        self.put_table(2, PyLexer.match_2, 4)

        self.put_table(3, PyLexer.match_3, None)

        self.put_table(4, PyLexer.match_4, 6)

        self.put_table(5, PyLexer.match_5, None)

        self.put_table(8, PyLexer.match_8, 10)

        self.put_table(9, PyLexer.match_9, 10)

        self.put_table(6, PyLexer.match_6, 10)

        self.put_table(7, PyLexer.match_7, None)

        self.put_table(10, PyLexer.match_10, None)

        self.put_table(11, PyLexer.match_11, None)

        self.put_table(12, PyLexer.match_12, None)

        self.put_table(13, PyLexer.match_13, None)


# -------------------
# Definitions end
# -------------------


# -------------------
# Rules start
# -------------------

    def rule_0(self):
        return COMMENT

    def rule_1(self):
        self.install_num(); return NUMBER

    def rule_2(self):
        return OPERATOR

    def rule_3(self):
        self.install_literal(); return STRING

    def rule_4(self):
        return WS

    def install_rules(self):

        self._rules[COMMENT] = PyLexer.rule_0

        self._rules[NUMBER] = PyLexer.rule_1

        self._rules[OPERATOR] = PyLexer.rule_2

        self._rules[STRING] = PyLexer.rule_3

        self._rules[WS] = PyLexer.rule_4

# -------------------
# Rules end
# -------------------


# -------------------
# User code starts
# -------------------

    def install_num(self):
        self.user_variables['number'] = int(self.yytoken())
    def install_literal(self):
        self.user_variables['literal'] = self.yytoken()

# -------------------
# User code ends
# -------------------


if __name__ == '__main__':
    import sys
    sm = PyLexer(sys.argv[1])
    while not sm.eof():
        print sm.nexttoken(), sm.yytoken()

