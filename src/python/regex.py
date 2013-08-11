"""
Regular expression matcher using NFA and DFA.

Reference: http://swtch.com/~rsc/regexp/regexp1.html

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

EPS   = ''

MATCH = 256 # Accepting state
SPLIT = 257 # Split state
ANY   = 258 # Matches any char

class Ptr(object):
    """
    Simulates C pointer.
    """
    counter = 0

    def __init__(self, value=None):
        self._value = value

        Ptr.counter += 1
        self._id = Ptr.counter

    def set_value(self, value):
        self._value = value

    def get_value(self):
        return self._value

    def id(self):
        return self._id

    def __repr__(self):
        return "Ptr%d(%s)" % (self._id, self._value if self._value is not None else "-")

class State(object):
    counter = 0

    def __init__(self, c, out=None, out1=None):
        State.counter += 1
        self.id   = State.counter
        self.c    = c
        self.out  = Ptr(out)  if out  is None or type(out)  != type(Ptr) else out
        self.out1 = Ptr(out1) if out1 is None or type(out1) != type(Ptr) else out1
        self.lastlist = 0

    def __repr__(self):
        def get_char(p):
            s = p.get_value()
            return s.c if s is not None else ""

        return "State%d(%s,Ptr%d(%s),Ptr%d(%s))" % \
            (self.id, self.c, self.out.id(), get_char(self.out), self.out1.id(),
             get_char(self.out1))

MATCH_STATE = State(MATCH) # Accepting state

class PtrList(object):
    """
    List of state pointers.
    """
    counter = 0

    def __init__(self, s=None):
        self.data = [s]

        PtrList.counter += 1
        self._id = PtrList.counter

    def patch(self, s):
        for si in self.data:
            si.set_value(s)

    def append(self, l2):
        for s in l2.data:
            self.data.append(s)
        return self

    def __repr__(self):
        return "Ptr[]%d(%s)" % (self._id, ",".join([str(s.get_value().c) for s in self.data]))

class Frag(object):
    def __init__(self, start, out):
        assert start is not None
        assert out is not None
        self.start = start
        self.out   = out

    def __repr__(self):
        return "Frag(%s, %s)" % (self.start, self.out)

def _post2nfa(postfix):
    """
    Convert postfix to NFA.
    """
    stack = []
        
    for i in range(postfix.size()):

        if postfix.is_concat(i):
            e2 = stack.pop()
            e1 = stack.pop()
            e1.out.patch(e2.start)
            stack.append(Frag(e1.start, e2.out))

        elif postfix.is_alt(i):
            e2 = stack.pop()
            e1 = stack.pop()
            s  = State(SPLIT, e1.start, e2.start)
            stack.append(Frag(s, e1.out.append(e2.out)))

        else:
            p = postfix.get(i)
            special = postfix.is_special(i)

            if special and p == '?':
                e = stack.pop()
                s = State(SPLIT, e.start)
                stack.append(Frag(s, e.out.append(PtrList(s.out1))))

            elif special and p == '*':
                e = stack.pop()
                s = State(SPLIT, e.start)
                e.out.patch(s)
                stack.append(Frag(s, PtrList(s.out1)))

            elif special and p == '+':
                e = stack.pop()
                s = State(SPLIT, e.start)
                e.out.patch(s)
                stack.append(Frag(e.start, PtrList(s.out1)))

            else:
                if postfix.is_any(i):
                    s = State(ANY)
                else:
                    s = State(p)
                stack.append(Frag(s, PtrList(s.out)))

    e = stack.pop()
    if stack:
        raise "Invalid regex postfix"
        
    e.out.patch(MATCH_STATE)

    return e.start


def e_closure(T, table):
    stack = [t for t in T]
    ec    = set([t for t in T])

    while stack:
        t   = stack.pop()
        row = table[t]
        if EPS in row:
            for u in row[EPS]:
                if u not in ec:
                    ec.add(u)
                    stack.append(u)

    return tuple(sorted(ec))


def enlist(x):
    return [x] if type(x) != list else x

def move(table, T, a):
    s = set([])

    for t in T:
        if a in table[t]:
            for si in enlist(table[t][a]):
                s.add(si)

    return tuple(sorted(s))


def nfa_to_dfa(table, s0, syms):
    def put(d_states, inv_d_dtates, U, mark=0):
        old = inv_d_states[1-mark]
        if U in old:
            old.remove(U)

        d_states[U] = mark
        inv_d_states[mark].add(U)

        return U

    def has_unmarked(d_states, inv_d_states):
        return len(inv_d_states[0]) > 0

    def extract_unmarked(d_states, inv_d_states):
        s = inv_d_states[0]
        return put(d_states, inv_d_states, s.pop(), 1)

    d_states     = {}
    inv_d_states = { 0 : set([]), 1 : set([]) }
    d_tran       = {}

    start = e_closure([s0], table)
    put(d_states, inv_d_states, start)

    while has_unmarked(d_states, inv_d_states):
        T = extract_unmarked(d_states, inv_d_states)
        if not T:
            continue

        for a in syms:
            U = e_closure(move(table, T, a), table)
            if U:
                if U not in d_states:
                    put(d_states, inv_d_states, U)

                d_tran.setdefault(T, {})
                d_tran.setdefault(U, {})
                d_tran[T][a] = U

    return start, d_tran

def transform(regex):
    regex2 = []

    i = 0
    n = len(regex)

    while i < n:
        c = regex[i]

        if c == '\\':
            assert i+1 < n
            regex2.append('\\')
            regex2.append(regex[i+1])
            i += 2
            continue
        
        if c != '[':
            regex2.append(c)
            i += 1
            continue

        regex2.append('(')

        l2 = []

        i += 1

        while i < n and regex[i] != ']':
            if i+2 < n and regex[i+1] == '-' and regex[i+1] != ']':
                cs = regex[i]
                ce = regex[i+2]
                for cj in range(ord(cs), ord(ce)+1):
                    l2.append(chr(cj))
                i += 3
            else:
                if regex[i] == '\\':
                    l2.append(regex[i:i+2])
                    i += 2
                else:
                    l2.append('\\' + regex[i])
                    i += 1

        assert regex[i] == ']'
        regex2.append("|".join(l2))
        regex2.append(')')

        i += 1

    return "".join(regex2)


class Regex(object):
    class Node(object):
        def __init__(self, natom=0, nalt=0):
            self.natom = natom
            self.nalt  = nalt

        def reset(self):
            self.natom = self.nalt = 0

        def incr_natom(self):
            self.natom += 1
            return self.natom

        def decr_natom(self):
            self.natom -= 1
            return self.natom

        def incr_nalt(self):
            nalt = self.nalt
            self.nalt += 1
            return nalt

        def decr_nalt(self):
            nalt = self.nalt
            self.nalt -= 1
            return nalt

    class Postfix(object):
        def __init__(self):
            self.postfix = []
            self.ctype   = {}

        def add(self, c):
            self.postfix.append(c)

        def special(self, c):
            self.ctype[len(self.postfix)] = c
            self.postfix.append(c)

        def alt(self):
            self.ctype[len(self.postfix)] = '|'
            self.postfix.append('|')

        def concat(self):
            self.ctype[len(self.postfix)] = ','
            self.postfix.append(',')

        def any(self):
            self.ctype[len(self.postfix)] = '.'
            self.postfix.append('.')

        def is_alt(self, i):
            return self.ctype.get(i, '') == '|'

        def is_concat(self, i):
            return self.ctype.get(i, '') == ','

        def is_any(self, i):
            return self.ctype.get(i, '') == '.'

        def is_special(self, i):
            return self.ctype.get(i, '') != ''

        def size(self):
            return len(self.postfix)

        def get(self, i):
            return self.postfix[i]

        def itr(self):
            for c in self.postfix:
                yield c
            
        def __repr__(self):
            return "".join(self.postfix)

    def __init__(self, pattern):
        self._pattern = transform(pattern)
        self._postfix = Regex._re2post(self._pattern)
        self._nfa     = _post2nfa(self._postfix)

        self._nfa_table, self._syms = self._construct_nfa_table()

        self._dfa_start, self._dfa_table = nfa_to_dfa(self.nfa_table(),
                                                      self.nfa_start(),
                                                      self.syms())


    def nfa_start(self):
        return self._nfa.id

    def dfa_start(self):
        return self._dfa_start

    def accepting(self):
        return MATCH_STATE.id

    def nfa_table(self):
        return self._nfa_table

    def dfa_table(self):
        return self._dfa_table

    def syms(self):
        return self._syms

    @staticmethod
    def _re2post(pattern):
        # Stack to maintain state per sub expression (enclosed in parenthesis).
        stack  = []
        # Current state node.
        curr   = Regex.Node()
        output = Regex.Postfix()

        # Go over input one char at a time.
        index = -1
        N     = len(pattern)
        while index < N-1:
            index += 1
            c = pattern[index]

            # Open parenthesis.
            if c == '(':
                if curr.natom > 1:
                    # Append previous pending concatenation.
                    curr.decr_natom()
                    output.concat()
                # Push the state on the stack.
                stack.append(Regex.Node(curr.natom, curr.nalt))
                curr.reset()

            # Close parenthesis.
            elif c == ')':
                if not stack:       raise "Mismatch in parenthesis"
                if curr.natom == 0: raise "Malformed pattern"
                # Flush pending inner concatenation.
                while curr.decr_natom() > 0:
                    output.concat()
                # Flush pending inner |.
                while curr.decr_nalt() > 0:
                    output.alt()
                # Pop previous state.
                curr = stack.pop()
                # Need to concatenate.
                curr.incr_natom()

            elif c == '|':
                if curr.natom == 0: raise "Malformed pattern"
                # Flush state before |.
                while curr.decr_natom() > 0:
                    output.concat()
                # Add | to pending state.
                curr.incr_nalt()

            elif c == '*' or c == '+' or c == '?':
                if curr.natom == 0: raise "Malformed pattern"
                # Add char c to output.
                output.special(c)

            else:
                any = c == '.'

                if c == '\\':
                    index += 1
                    assert index < N
                    c = pattern[index]
                
                # Append previous pending concatenation.
                if curr.natom > 1:
                    curr.decr_natom()
                    output.concat()
                # Add char c to output.
                if any:
                    output.any()
                else:
                    output.add(c)
                # Need to concatenate.
                curr.incr_natom()
      
        if stack: raise "Mismatch in parenthesis"

        # Flush pending concatenation.
        while curr.decr_natom() > 0:
            output.concat()
        # Flush pending |.
        while curr.decr_nalt() > 0:
            output.alt()

        return output

    listid = 0

    def nfa_match(self, input):
        """
        Check whether regex matches the input using NFA.
        """
        Regex.listid += 1
        clist = self._start_list(self._nfa)

        for s in input:
            clist = self._step(clist, s)
    
        return self._is_match(clist)

    def _is_match(self, l):
        for s in l:
            if s == MATCH_STATE:
                return True
        return False

    def _add_state(self, l, s):
        if s is None or s.lastlist == Regex.listid:
            return

        s.lastlist = Regex.listid
        if s.c == SPLIT:
            self._add_state(l, s.out.get_value())
            self._add_state(l, s.out1.get_value())
            return
        l.append(s)

    def _start_list(self, s):
        Regex.listid += 1
        l = []
        self._add_state(l, s)
        return l

    def _step(self, clist, c):
        Regex.listid += 1
        nlist = []
        for s in clist:
            if s.c == c or s.c == ANY:
                self._add_state(nlist, s.out.get_value())
        return nlist

    @staticmethod
    def _recursive_construct_nfa_table(table, s, states):
        if s is None or s.id in states or s.c == MATCH:
            return

        states.add(s.id)
        m = table.setdefault(s.id, {})

        if s.c == SPLIT:
            m[EPS] = [s.out.get_value().id, s.out1.get_value().id]
            Regex._recursive_construct_nfa_table(table, s.out.get_value(), states)
            Regex._recursive_construct_nfa_table(table, s.out1.get_value(), states)
            return

        m[s.c] = s.out.get_value().id
        Regex._recursive_construct_nfa_table(table, s.out.get_value(), states)

    def _construct_nfa_table(self):
        states = set([])
        table  = {}

        table[MATCH_STATE.id] = {}
        
        Regex._recursive_construct_nfa_table(table, self._nfa, states)

        syms = set([])
        for _, row in table.items():
            for c in row:
                if c != EPS:
                    syms.add(c)

        return table, syms

    def print_nfa_table(self):
        t = self.nfa_table()
        print "NFA table:"
        for s in sorted(t):
            print s, t[s]

    def print_dfa_table(self):
        t = self.dfa_table()
        print "DFA table:"
        for s in sorted(t):
            print s, t[s]

    def dfa_match(self, input):
        state = self.dfa_start()
        table = self.dfa_table()

        for i in input:
            row = table[state]
            if i in row:
                state = row[i]
            elif ANY in row:
                state = row[ANY]
            else:
                return False

        return self.accepting() in state


from contextlib import contextmanager
import datetime

@contextmanager
def timeit(name, n=1):
    d1 = datetime.datetime.now()
    yield
    d2 = datetime.datetime.now()
    dt = (d2 - d1)
    print "%s: #loops=%d time=%.2fms" % (name, n, dt.seconds * 1000.0 + dt.microseconds / 1000.0)


if __name__ == '__main__':
    import sys
    import re

    print transform(sys.argv[1])

    r1 = Regex(sys.argv[1])
    r2 = re.compile(sys.argv[1])

    r1.print_nfa_table()
    r1.print_dfa_table()

    for input in sys.argv[2:]:
        print input, r1.dfa_match(input)

    for input in sys.argv[2:]:
        print input, r1.nfa_match(input)

    if len(sys.argv) <= 2:
        exit()

    input = sys.argv[2]
    
    with timeit("dfa_match"):
        r1.dfa_match(input)

    with timeit("nfa_match"):
        r1.nfa_match(input)

    with timeit("re"):
        r2.match(input)

