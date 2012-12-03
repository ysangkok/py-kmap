#!/usr/bin/env python3.3

import pydot
from lispify import dump, listit, tupleit
import ast
import sys
import itertools
import operator
from collections import Iterable

def repeated(f, lst):
    def rfun(p):
        for a in lst:
            p = f(p,a)
        return p
    return rfun

class Name(object):
  def __init__(self, g, name):
    self.name = name
    self.g = g
    self.manifested = False
  def manifest(self, counter):
    if not self.manifested:
      self.node = pydot.Node(id(self), label=self.name, id="name-node-{}".format(next(counter)))
      self.g.add_node(self.node)
      self.manifested = True
  def __repr__(self):
    return self.__class__.__name__ + "(" + self.name + ")"
  def __eq__(self, other):
    return isinstance(other, Name) and self.name == other.name
  def __hash__(self):
    return hash(self.name)

class LogicalFunction(object):
  def __repr__(self):
    return "{}({})".format(self.op, ", ".join([repr(i) for i in self.ops]))
  def __eq__(self, other):
    return isinstance(other, LogicalFunction) and self.ops == other.ops and self.op == other.op
  def __hash__(self):
    return hash(self.op) ^ hash(tuple(self.ops))

  def __init__(self, g, op, ops):
    #if len(ops) == 1: assert op == "Not"
    self.op = op
    self.g = g
    self.ops = ops
    for i in self.ops: assert isinstance(i, LogicalFunction) or isinstance(i, Name), self.ops
    self.manifested = False

  def getops(self):
    return self.ops

  def manifest(self, counter):
   if not self.manifested:
    for o in self.ops: o.manifest(counter)
    self.node = pydot.Node(id(self), label=self.op, id="logifunc-node-{}".format(next(counter)))
    self.g.add_node(self.node)
    for o in self.ops: self.g.add_edge(pydot.Edge(self.node, o.node, id="edge-{}".format(next(counter))))
    self.manifested = True

def onlylists(elem):
	return type(elem) == list

def is_ok(lst):
	""" lst contains only lists of simple elements """
	if type(lst) != list: return False
	listsinme = list(filter(onlylists, lst))
	if len(listsinme) == 0: return False
	elemsofsublists = itertools.chain.from_iterable(map(lambda x: filter(onlylists, x), listsinme))
	onlyhassimple = all(map(lambda x: type(x) != list, elemsofsublists))
	return onlyhassimple

def get_simplest(outer):
	def worker(lst,sofar):
		if is_ok(lst): yield sofar
		if type(lst) == list:
			coun = 0
			for i in lst:
				yield from worker(i,tuple(list(sofar)+[coun]))
				coun = coun + 1
	return list(worker(outer,()))

def source_to_graph(source, counter):
  def objectify(le, names):
    op = le[0]
    rest = le[1:]
    #if len(rest) == 1: rest = rest[0]
    found = None
    for i in names:
      if isinstance(i, LogicalFunction) and i.op == op and i.getops() == rest:
        found = i
        break
    if found is None:
      new = LogicalFunction(g, op, rest)
      names = frozenset(list(names) + [new])
      return (new, names)
    return (found, names)

  def walktree(lisp, sett):
    if len(lisp) > 0 and lisp[0] == "Name":
      found = None
      for i in sett:
        if i.name == lisp[1]:
          found = i
          break
      if found is None:
        name = Name(g, lisp[1])
        return (name, frozenset(list(sett)+[name]))
      return (found, sett)
    if type(lisp) == str:
      return (lisp, sett)
    newlispcol = []
    for i in lisp:
      (newlisp, newset) = walktree(i,sett)
      newlispcol += [newlisp]
      sett = newset
    return newlispcol, sett

  g = pydot.Dot(id="graph-{}".format(next(counter)))
  g.set_type('digraph')

  lisp = listit(dump(ast.parse(source)))
  (lisp, names) = walktree(lisp,frozenset()) # objectify names

  #objectifier = lambda x: list(map(lambda y: deepest[i] if type(y) == list else objectify(y), x))

  if not isinstance(lisp, Iterable):
    lisp.manifest(counter)
    return g

  """ objectify deepest first """
  while True:
    indices = get_simplest(lisp)
    if indices == []: break
    for k in indices:
     j = repeated(operator.getitem, k)(lisp)
     for i in range(len(j)):
      if type(j[i]) == list:
       (j[i], names) = objectify(j[i], names)

  for i in range(len(lisp)):
    if type(lisp[i]) == list:
      (lisp[i], names) = objectify(lisp[i], names)
    
  (lisp, names) = objectify(lisp, names)

  lisp.manifest(counter)

  return g

def test():
  sys.setrecursionlimit(40)
  assert not is_ok(3)
  assert not is_ok([3])
  assert not is_ok([[1,2],[3,[4,5]]])
  assert is_ok([3,[4,5]])
  simp = get_simplest([[1,2],[3,[4,5]]])
  assert simp == [(1,)], simp

  from tempfile import NamedTemporaryFile

  org = [1,[2,[3,4,5]],[6,7,[8,[9]]]]
  res = [x(org) for x in [repeated(operator.getitem, k) for k in get_simplest(org)]]
  assert [8,[9]] in res, res

  g = source_to_graph("(a | a | a) & (a | a | a)")

  with NamedTemporaryFile(delete=False) as f:
    a = g.create(format='jpe')
    f.write(a)
    print(f.name)

if __name__ == "__main__":
  test()
