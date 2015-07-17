# -*- coding: utf-8 -*-

from flask import request
from flask.ext import restful
from flask.ext.restful import reqparse

from geospatial.common.Record import Record

# Argument parser for the GET method. All args are optional
parser_get = reqparse.RequestParser()
parser_get.add_argument('decimalLatitude', type=float, location='args')
parser_get.add_argument('decimalLongitude', type=float, location='args')
parser_get.add_argument('countryCode', location='args')
parser_get.add_argument('scientificName', location='args')

# Argument parser for the POST method. The 'records' arg is mandatory
parser_post = reqparse.RequestParser()
parser_post.add_argument(
    'records',
    type=list,
    required=True,
    location='json',
    help="Must provide a list of records"
)

class Geospatialissue(restful.Resource):

    def get(self):

        args = parser_get.parse_args()

        record = Record(args)
        flags = record.parse()
        args['flags'] = flags

        return args, 201

    def post(self):

        args = parser_post.parse_args()
        records = args['records']

        for i in range(len(records)):

            record = Record(records[i])
            
            flags = record.parse()

            records[i]['flags'] = flags

        return records, 201

