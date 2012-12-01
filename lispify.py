#!/usr/bin/env python3.3
import ast
from ast import AST, iter_fields
import json
import collections

iterable = lambda x: isinstance(x, collections.Iterable)

def listit(t):
            if isinstance(t, str): return t
            if isinstance(t, tuple):
              return tuple(map(listit, t)) if iterable(t) else t
            return list(map(listit, t)) if iterable(t) else t

def flatten(L):
  for e in L:
    if isinstance(e, Iterable):
      yield from flatten(e)
    else:
      yield e 

def dump(node, annotate_fields=True, include_attributes=False):
    def _format(node):
        #yield node.__class__.__name__
        if isinstance(node, AST):
            clazz = node.__class__.__name__
            fields = dict([(a, _format(b)) for a, b in iter_fields(node)])
            if clazz == "UnaryOp":
              yield from fields["op"]
              yield fields["operand"]
            elif clazz == "Name":
              yield list(fields["id"])[0]
            elif clazz == "BoolOp":
              yield from fields["op"]
              yield from fields["values"]
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
        yield node
        return
    if not isinstance(node, AST):
        raise TypeError('expected AST, got %r' % node.__class__.__name__)
    #yield from _format(node)
    return list(_format(node))[0] # only one statement

#print(json.dumps(listit(dump(ast.parse("a or b and c"))), indent=2))
print(listit(dump(ast.parse("abe or not (b and c)"))))
print(listit(dump(ast.parse("a & b & c"))))
print(listit(dump(ast.parse("a & ~b & c"))))
print(listit(dump(ast.parse("a << c; -a")))) # -a discarded
print(listit(dump(ast.parse("-a"))))
print(listit(dump(ast.parse("a <= b < c == d"))))
#print(listit([('hej','med'),('dig',)]))


