#!/usr/bin/env python3.3
import ast
from ast import AST, iter_fields
import json
import collections
from itertools import chain
import itertools
from colors import chunks
from functools import reduce
import sys

iterable = lambda x: isinstance(x, collections.Iterable)

def listit(t):
  if isinstance(t, str): return t
  if isinstance(t, tuple):
    return tuple(map(listit, t)) if iterable(t) else t
  return list(map(listit, t)) if iterable(t) else t

def tupleit(t):
  if isinstance(t, str): return t
  return tuple(map(tupleit, t)) if iterable(t) else t

flatten = itertools.chain.from_iterable

def duplicate_elements_except_last_and_first(variables):
	variables = list(variables)
	return chain([variables[0]], flatten([x,x] for x in variables[1:len(variables)-1]), [variables[-1]])

def dump(node):
    def _format(node):
        #yield node.__class__.__name__
        if isinstance(node, AST):
            clazz = node.__class__.__name__
            fields = dict([(a, _format(b)) for a, b in iter_fields(node)])
            if clazz == "UnaryOp":
              yield from fields["op"]
              yield fields["operand"]
            elif clazz == "Compare":
              variables = chain([fields["left"]], (list(x) for x in fields["comparators"]))
              variables = map(list,variables) # ['Name','a'] format
              variables = chunks(duplicate_elements_except_last_and_first(variables),2)
              variables = map(flatten,zip(fields["ops"], variables))
              variables = reduce(lambda x, y: ["And", x, y], variables) # and-tree of 2-way-ands instead of giant and-gate
              yield from variables
            elif clazz == "Name":
              yield clazz
              li = list(fields["id"])
              yield li[0]
            elif clazz == "BoolOp":
              yield from fields["op"]
              yield from fields["values"]
              #yield from reduce(lambda x, y: [fields["op"], x, y], fields["values"])
            elif clazz == "BinOp":
              yield from fields["op"]
              yield fields["left"]
              yield fields["right"]
            elif clazz == "Module":
              yield from fields["body"]
            elif clazz == "Expr":
              yield from fields["value"]
            else:
              yield clazz
              yield from fields.items()
            return
        elif isinstance(node, list):
            yield from (_format(x) for x in node)
            return
        yield node # f.eks. "abe"
        return
    if not isinstance(node, AST):
        raise TypeError('expected AST, got %r' % node.__class__.__name__)
    #yield from _format(node)
    return list(_format(node))[0] # only one statement

if __name__ == "__main__":
  from srcdot import source_to_graph
  from subprocess import Popen, PIPE, STDOUT
  def fun(x):
    print(x)
    svg = source_to_graph(x).create(format="svg")
    p = Popen(['display', '-'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    return p.communicate(input=svg)[0].decode("UTF-8")
    return svg.decode("UTF-8")
  fun2 = lambda x: listit(dump(ast.parse(x)))
  print(fun2("a and b and c"))
  sys.exit()
  print(json.dumps(list(map(fun, [
  "a or b and c",
  "abe or not (b and c)",
  "a & b & c",
  "a & ~b & c",
  "a << c; -a", # -a discarded
  "-a",
  "a <= b < c == d",
  "a ** d",
  ])), indent=4))
  #print(listit([('hej','med'),('dig',)]))


