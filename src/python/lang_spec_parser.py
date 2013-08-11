"""
LANG specifiction file parser.

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

Structure:

%%Constants%%

%%Definitions%%

WS: [ \t\n\r]

NUMBER: [0-9]+

OPERATOR: [-+*/]

%%Rules%%

NUMBER: self.install_num(); return NUMBER

OPERATOR: return OPERATOR

%%Code%%

def install_num(self):
    self.user_variables['number'] = int(self.yytoken())

Author: Mayur P Srivastava
"""

# ------------------------

from __future__ import division

import logging
import re

# ------------------------

CONSTANT_PATTERN = re.compile("^(.+?)\s*$")
CONSTANT_SPLIT_PATTERN = re.compile("\\n")
CONSTANT_KEY_VALUE_PATTERN = re.compile("^([^\s=]+)\s*=\s*([^\s]+)$")

DEFINITION_PATTERN = re.compile("^([A-Za-z][A-Za-z0-9_]+):\s*(.+)$")
CONT_DEFINITION_PATTERN = re.compile("^\s+(.+)$")

RULE_PATTERN = re.compile("^([^:]+):\s*(.+?)\s*$")

# ------------------------

def warn(m):
    logging.warn(m)

def info(m):
    logging.info(m)

def parse_warn(line):
    warn("[IGNORING] Failed to parse line '%s'" % line)

# ------------------------

class Section(object):
    def __init__(self, section, next=None):
        self.section = section
        self.lcname  = section.lower()
        self.next    = next

    def set_next(self, next):
        self.next = next

    def __repr__(self):
        return self.section


CODE        = Section("%%CODE%%")
RULES       = Section("%%RULES%%", CODE)
DEFINITIONS = Section("%%DEFINITIONS%%", RULES)
CONSTANTS   = Section("%%CONSTANTS%%", DEFINITIONS)
UNKNOWN     = Section("UNKNOWN", CONSTANTS)

# ------------------------

def parse(fn):
    constants = {}

    definitions_order = []
    definitions = {}

    rules = {}

    code = []

    section = UNKNOWN

    with open(fn) as fh:
        for line in fh:
            line = line.rstrip()
            if not line or line.startswith("#"):
                continue

            if section is None:
                raise "Bad state"
            
            if section.next and line.lstrip().lower().startswith(section.next.lcname):
                section = section.next
                info("Starting section: %s" % section)
                continue
            
            if section == CONSTANTS:
                m = CONSTANT_PATTERN.match(line)
                if not m:
                    parse_warn(line)
                    continue

                for c in CONSTANT_SPLIT_PATTERN.split(m.groups()[0]):
                    m = CONSTANT_KEY_VALUE_PATTERN.match(c)
                    if not m:
                        parse_warn(line)
                        continue

                    ck = m.groups()[0]
                    cv = m.groups()[1]

                    constants[ck] = cv

                continue

            elif section == DEFINITIONS:
                if definitions_order:
                    m = CONT_DEFINITION_PATTERN.match(line)
                    if m:
                        defn = m.groups()[0]
                        definitions[definitions_order[-1]].append(defn)
                        info("Appending to def %s: %s" % (definitions_order[-1], defn))
                        continue

                m = DEFINITION_PATTERN.match(line)
                if not m:
                    parse_warn(line)
                    continue
                last_defn = m.groups()[0]
                defn      = m.groups()[1]
                info("Adding def %s: %s" % (last_defn, defn))
                definitions_order.append(last_defn)
                definitions[last_defn] = [defn]

            elif section == RULES:
                m = RULE_PATTERN.match(line)
                if not m:
                    parse_warn(line)
                    continue

                rules[m.groups()[0]] = m.groups()[1]

            elif section == CODE:
                code.append(line)

    return constants, [(i, definitions[i]) for i in definitions_order], rules, code


if __name__ == '__main__':
    import sys
    logging.getLogger().setLevel('INFO')

    constants, definitions, rules, code = parse(sys.argv[1])
    print constants
    print definitions
    print rules
    print code
