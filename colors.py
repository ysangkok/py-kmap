#!/usr/bin/env python3.3
import colorsys
import itertools
from fractions import Fraction
import math
import json
import collections

F = Fraction
flatten = itertools.chain.from_iterable

def zenos_dichotomy():
	"""
	http://en.wikipedia.org/wiki/1/2_%2B_1/4_%2B_1/8_%2B_1/16_%2B_%C2%B7_%C2%B7_%C2%B7
	"""
	for k in itertools.count():
		yield F(1,2**k)

def genfracs():
  """
  [Fraction(0, 1), Fraction(1, 2), Fraction(1, 4), Fraction(3, 4), Fraction(1, 8), Fraction(3, 8), Fraction(5, 8), Fraction(7, 8), Fraction(1, 16), Fraction(3, 16), ...]
  [0.0, 0.5, 0.25, 0.75, 0.125, 0.375, 0.625, 0.875, 0.0625, 0.1875, ...]
  """
  yield 0
  for k in zenos_dichotomy():
    i = k.denominator # [1,2,4,8,16,...]
    for j in range(1,i,2):
      yield F(j,i)

bias = lambda x: (math.sqrt(x/3)/F(2,3)+F(1,3))/F(6,5) # can be used for the v in hsv to map linear values 0..1 to something that looks equidistant

def genhsv(h): 
	for s in [F(6,10)]: # optionally use range
		for v in [F(8,10),F(5,10)]: # could use range too
			yield (h, s, v) # use bias for v here if you use range
def genrgb(x):
	for z in x: assert 0<=z<1
	return colorsys.hsv_to_rgb(*x)

def chunks(iterable,size):
    """ http://stackoverflow.com/a/434314/309483 """
    it = iter(iterable)
    chunk = tuple(itertools.islice(it,size))
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(it,size))

def intersperse(lot):
	# [(1,2),(3,4)] => [1, 3, 2, 4]
	return flatten(zip(*lot))

def reorder(hsvs):
	"""
	reorder (mix within intervals) colors to avoid having colors with the same hue but different lightness next to each other

  [(0, 1, 2), (3, 4, 5), (6, 7, 8), ...]

        =>

  [[0, 3, 6, 9, 12, 15, 18, 21, 1, 4, 7, 10, 13, 16, 19, 22, 2, 5, 8, 11, 14, 17, 20, 23], [24, ...], ...]

	"""
	return (intersperse(x) for x in chunks(hsvs,8))

def gethsvtuples():
	return map(genhsv,genfracs())

def gethsvs():
	return flatten(reorder(gethsvtuples()))

def getrgbs():
	return map(genrgb, gethsvs())

iterable = lambda x: isinstance(x, collections.Iterable)

def recursiveflatten(x):
        return [a for i in x for a in recursiveflatten(i)] if iterable(x) else [x]

def test_reorder():
  org = [(i*3,i*3+1,i*3+2) for i in range(2*8+2)]
  print(org)
  new = list(map(list,reorder(org)))
  print(new)
  assert len(set(recursiveflatten(new))) == len(recursiveflatten(new))

def listit(js=True):
	def tmp(t):
	    if js:
	      if isinstance(t, Fraction): return float(t) 
	    return list(map(tmp, t)) if iterable(t) else t
	if not js:
		return tmp
	else:
		return lambda x: json.dumps(tmp(x))

def outputfriendly(i): return listit(js=False)(i)

if __name__ == "__main__":
  print(outputfriendly(itertools.islice(genfracs(), 3)))
  print(outputfriendly(itertools.islice(gethsvs(), 3)))
  print(outputfriendly(itertools.islice(getrgbs(), 3)))

  #test
  test_reorder()

  inst = genfracs()
  s = set()
  
  for i in range(pow(2,18)):
  	try:
  		col = next(inst)
  		if col in s: raise Exception("known colour:",col)
  		s.add(col)
  	except StopIteration:
  		raise Exception("should be infinite!")
  
