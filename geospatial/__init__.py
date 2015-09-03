from flask import Flask
from flask.ext import restful

from geospatial.resources.geospatialissue import Geospatialissue, SingleRecord

app = Flask(__name__)
api = restful.Api(app)

api.add_resource(Geospatialissue, '/geospatialissue')
api.add_resource(SingleRecord, '/singlerecord')