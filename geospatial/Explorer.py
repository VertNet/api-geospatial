import webapp2

__author__ = '@jotegui'


class GeospatialExplorerHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write('Hello, World!')