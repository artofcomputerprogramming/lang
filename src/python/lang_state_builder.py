"""
Builds the lexical analyzer state machine.

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

class Counter(object):
    def __init__(self, init=0):
        self.i = init

    def postincr(self):
        i = self.i
        self.i += 1
        return i

    def get(self):
        return self.i

class Builder(object):
    def __init__(self, code_gen):
        assert isinstance(code_gen, lang_codegen.LangCodeGen)
        self.codegen = code_gen

        self.code = self.codegen.common_code()
        self.transitions = []
    
    def common_code(self):
        self.code += self.codegen.common_code()

    def _dfa_state_matcher_gen(self, dfa_table, dfa_start, start_state, definition):
        def _map(mapping, si, counter):
            if si not in mapping:
                i = counter.postincr()
                mapping[si] = i
                return i
            return mapping[si]

        counter = Counter(start_state)
        mapping = {}

        _map(mapping, dfa_start, counter)

        transitions = {}
        fail_states = {}
        
        class_name = self.codegen.class_name()

        code = ""

        for si in sorted(dfa_table):
            sij = _map(mapping, si, counter)
            row = dfa_table[si]

            accepting = regex.MATCH_STATE.id in si

            code += self.codegen.match_fn_start(sij, len(row)>0)

            # Move . (any) to the end.
            ordered_row = []
            for r in row:
                if r != regex.ANY:
                    ordered_row.append(r)
            ordered_row = sorted(ordered_row)
            has_any = False
            if regex.ANY in row:
                has_any = True
                ordered_row.append(regex.ANY)

            for k in ordered_row:
                nextsi  = row[k]
                nextsij = _map(mapping, nextsi, counter)

                code += self.codegen.match_fn_condition(k, nextsij)

            if not has_any:
                code += self.codegen.match_fn_end(accepting, definition, len(row)>0)

            fn_name = "%s.%s" % (class_name, self.codegen.match_fn_name(sij))
            transitions[sij] = fn_name
            fail_states[sij] = not accepting

        for sij, fn_name in transitions.items():
            self.transitions.append([sij, 
                                     fn_name,
                                     counter.get() if fail_states[sij] else None])

        return code, counter.get()

    def build(self, laststate):
        self.code += self.codegen.transitions_fn(self.transitions, laststate)

        return self.code

    def add_regex(self, r, start_state, definition):
        r2 = regex.Regex(r)

        code, next_state = self._dfa_state_matcher_gen(r2.dfa_table(),
                                                       r2.dfa_start(),
                                                       start_state,
                                                       definition)

        self.code += code

        return next_state


if __name__ == '__main__':
    import sys
    import pylang_codegen

    r = regex.Regex(sys.argv[1])

    builder = Builder(pylang_codegen.PyLangCodeGen())
    nextstate = 0
    nextstate = builder.add_regex(sys.argv[1], nextstate)
    print builder.build(nextstate)
