"""Tests for refleaks."""

import itertools

from cherrypy._cpcompat import HTTPConnection, HTTPSConnection
import threading

import cherrypy


data = object()


from cherrypy.test import helper


class ReferenceTests(helper.CPWebCase):

    @staticmethod
    def setup_server():

        class Root:

            @cherrypy.expose
            def index(self, *args, **kwargs):
                cherrypy.request.thing = data
                return "Hello world!"

        cherrypy.tree.mount(Root())

    def test_threadlocal_garbage(self):
        success = itertools.count()

        def getpage():
            host = '%s:%s' % (self.interface(), self.PORT)
            if self.scheme == 'https':
                c = HTTPSConnection(host)
            else:
                c = HTTPConnection(host)
            try:
                c.putrequest('GET', '/')
                c.endheaders()
                response = c.getresponse()
                body = response.read()
                self.assertEqual(response.status, 200)
                self.assertEqual(body, b"Hello world!")
            finally:
                c.close()
            next(success)

        ITERATIONS = 25

        ts = [
            threading.Thread(target=getpage)
            for _ in range(ITERATIONS)
        ]

        for t in ts:
            t.start()

        for t in ts:
            t.join()

        self.assertEqual(next(success), ITERATIONS)
