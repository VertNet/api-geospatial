from flask import Flask
from flask.ext import restful

from geospatial.resources.geospatialissue import Geospatialissue
from geospatial.common import *

app = Flask(__name__)
api = restful.Api(app)

api.add_resource(Geospatialissue, '/geospatialissue')

