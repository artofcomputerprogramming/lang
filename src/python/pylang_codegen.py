"""
Python specific implementation of LangCodeGen.

Author: Mayur P Srivastava


Copyright (C) Mayur P Srivastava

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import lang_codegen
import regex

class PyLangCodeGen(lang_codegen.LangCodeGen):
    def __init__(self):
        pass

    def common_code(self):
        return """
class LangException(Exception):
    def __init__(self, line, message):
        self.line = line
        self.msg  = message

    def __str__(self):
        return self.msg + ":\\n" + self.line

class %s(object):
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
        start  = max(start, data.rfind("\\n"))
        length = min(self.input_index, len(self.input)) + 1 - start
        data   = data + "\\n" + ("-" * (length-1)) + "^"
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
""" % self.class_name()

    def class_name(self):
        return "PyLexer"

    def match_fn_name(self, state):
        return "match_%d" % state

    def match_fn_start(self, state, has_conditions=True):
        code = """
    def %s(self):
""" % self.match_fn_name(state)

        if has_conditions:
            code += """
        c = self.nextchar()
"""

        return code

    def match_fn_condition(self, c, nextstate):
        if c != regex.ANY:
            return """
        if c == '%s':
            self.curr_state = %d
            return
""" % (c, nextstate)
        else:
            return """
        self.curr_state = %d
        return
""" % nextstate

    def match_fn_end(self, accepting, definition, should_retract=True):
        if accepting:
            return """
        %s
        return self.matched(%s)
""" % ("self.retract()" if should_retract else "", definition)
        else:
            return """
        %s
        self.curr_state = self.fail()
""" % ("self.retract()" if should_retract else "")

    def transitions_fn(self, transitions, laststate):
        code = """
    def install_transitions(self):
"""
        for state, fn, nextstate in transitions:
            code += """
        self.put_table(%d, %s, %s)
""" % (state, fn, nextstate if nextstate != laststate else None)

        return code

    def add_main(self):
        return """
if __name__ == '__main__':
    import sys
    sm = %s(sys.argv[1])
    while not sm.eof():
        print sm.nexttoken(), sm.yytoken()
""" % self.class_name()

    def add_header(self, spec):
        return """
\"\"\"
Lexical analyzer.

Generated from '%s' by LANG.
\"\"\"
""" % spec

    def add_constants(self, constants):
        code = """
# -------------------
# Constants start
# -------------------
"""
        for c in sorted(constants):
            i = constants[c]
            code += """
%s = %s
""" % (c, i)

        code += """
# -------------------
# Constants end
# -------------------
"""
        return code
    
    def add_rules(self, rules):
        code = """
# -------------------
# Rules start
# -------------------
"""

        m = {}

        for i, rule in enumerate(sorted(rules)):
            c       = rules[rule]
            fn_name = "rule_%d" % i
            m[rule] = fn_name

            code += """
    def %s(self):
        %s
""" % (fn_name, c)

        if rules:
            code += """
    def install_rules(self):
"""

            class_name = self.class_name()
        
            for rule in sorted(rules):
                code += """
        self._rules[%s] = %s.%s
""" % (rule, class_name, m[rule])

        else:
            code += """
    def install_rules(self):
        pass
"""

        code += """
# -------------------
# Rules end
# -------------------
"""

        return code

    def add_code(self, code):
        return """
# -------------------
# User code starts
# -------------------

%s

# -------------------
# User code ends
# -------------------
""" % "\n".join(["    %s" % c for c in code])
    
    def definitions_start(self):
        return """
# -------------------
# Definitions start
# -------------------
"""

    def definitions_end(self):
        return """
# -------------------
# Definitions end
# -------------------
"""

