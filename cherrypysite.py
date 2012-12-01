#!/usr/bin/env python3.3
import truth
import cherrypy
from cgi import MiniFieldStorage
 
class HelloWorld(object):
    def index(self, **kwargs):
        #return "".join(truth.servepage("/", dict([(x, MiniFieldStorage(x,y)) for x,y in kwargs.items()])))
        yield from truth.servepage("/", dict([(x, MiniFieldStorage(x,y)) for x,y in kwargs.items()]))
    index.exposed = True
    index._cp_config = {'response.stream': True}
 
cherrypy.quickstart(HelloWorld())

