"""
LANG - python Lexical ANalizer Generator.

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

import pylang_codegen
import lang_spec_parser
import lang_state_builder

class Lang(object):
    def __init__(self, spec, outfn, codegen):
        assert spec    is not None
        assert outfn   is not None
        assert codegen is not None
        self.spec    = spec
        self.outfn   = outfn
        self.codegen = codegen

    def generate(self):
        constants, definitions_mapping, rules, code = lang_spec_parser.parse(self.spec)

        i = 1
        for defn, _ in definitions_mapping:
            if defn not in constants:
                constants[defn] = i
                i += 1

        with open(self.outfn, "w") as fh:
            print >>fh, self.codegen.add_header(self.spec)
            print >>fh, self.codegen.add_constants(constants)

            builder = lang_state_builder.Builder(self.codegen)

            print >>fh, self.codegen.definitions_start()

            nextstate = 0
            for defn, patterns in definitions_mapping:
                pattern = "|".join(patterns)
                nextstate = builder.add_regex(pattern, nextstate, defn)

            print >>fh, builder.build(nextstate)

            print >>fh, self.codegen.definitions_end()

            print >>fh, self.codegen.add_rules(rules)

            print >>fh, self.codegen.add_code(code)

            print >>fh, self.codegen.add_main()

if __name__ == '__main__':
    import sys

    lex = Lang(sys.argv[1], sys.argv[2], pylang_codegen.PyLangCodeGen())
    lex.generate()
