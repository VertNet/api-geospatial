from flask.ext import restful
from flask.ext.restful import reqparse
from flask.ext.restful import fields, marshal_with

from geospatial.common.util import cdbQuery

# Argument parser for single-record queries
single_record_parser = reqparse.RequestParser()
single_record_parser.add_argument('latitude',
                                  type=float,
                                  help='Latitude value in decimal degrees, positive for North, negative for South (e.g. 42.123)',
                                  required=True,
                                  location='args',
                                  dest='decimalLatitude'
)
single_record_parser.add_argument('longitude',
                                  type=float,
                                  help='Longitude value in decimal degrees, positive for East, negative for West (e.g. -1.883)',
                                  required=True,
                                  location='args',
                                  dest='decimalLongitude'
)
single_record_parser.add_argument('countrycode',
                                  type=unicode,
                                  help='Country code, in 2 or 3 letter form (e.g. US or USA)',
                                  location='args',
                                  dest='countryCode',
                                  default=''
)


resource_fields = {
    'decimalLatitude': fields.Float,
    'decimalLongitude': fields.Float,
    'countryCode': fields.String,
    'noCoordinates': fields.Boolean(attribute='nocoordinates'),
    'noCountry': fields.Boolean(attribute='nocountry'),
    'isZero': fields.Boolean(attribute='iszero'),
    'isOutOfWorld': fields.Boolean(attribute='isoutofworld'),
    'isLowPrecision': fields.Boolean(attribute='islowprecision'),
    'isOutOfCountry': fields.Boolean(attribute='isoutofcountry'),
    'isTransposed': fields.Boolean(attribute='istransposed'),
    'isNegatedLatitude': fields.Boolean(attribute='isnegatedlatitude'),
    'isNegatedLongitude': fields.Boolean(attribute='isnegatedlongitude'),
    'distanceToCountry': fields.Float(attribute='distance2country')
}


class Geospatialissue(restful.Resource):
    @marshal_with(resource_fields)
    def get(self):
        args = single_record_parser.parse_args()
        q = "select (geospatial_issue({0}, {1}, '{2}')).*".format(args['decimalLatitude'], args['decimalLongitude'], args['countryCode'])
        cdb_resp = cdbQuery(q)[0]
        resp = args.copy()
        resp.update(cdb_resp)
        return resp
