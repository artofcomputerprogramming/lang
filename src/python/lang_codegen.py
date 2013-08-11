"""
Interface for code generator.

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

class LangCodeGen(object):
    @staticmethod
    def nyi():
        raise "Not Yet Implemented"
    
    def class_name(self):
        CodeGen.nyi()

    def add_header(self, spec):
        CodeGen.nyi()

    def common_code(self):
        CodeGen.nyi()

    def match_fn_start(self, state, has_conditions):
        CodeGen.nyi()

    def match_fn_condition(self, c, nextstate):
        CodeGen.nyi()

    def match_fn_end(self, accepting, definition, should_retract):
        CodeGen.nyi()
    
    def transitions_fn(self, transitions, laststate):
        CodeGen.nyi()

    def add_main(self):
        CodeGen.nyi()

    def add_constants(self, constants):
        CodeGen.nyi()
    
    def add_rules(self, rules):
        CodeGen.nyi()

    def add_code(self, code):
        CodeGen.nyi()

    def definitions_start(self):
        CodeGen.nyi()

    def definitions_end(self):
        CodeGen.nyi()
        
