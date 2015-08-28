#!/usr/bin/env python3.3
import itertools
from colors import getrgbs
import cgitb

cgitb.enable()

print("Content-Type: text/html")
print()

print("<html><body>")

for color in itertools.islice(getrgbs(),100):
    print("<div style='background-color: rgb({},{},{});'>hello world</div>".format(*map(lambda x: int(x*255), color)),end="")
