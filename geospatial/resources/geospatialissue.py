# -*- coding: utf-8 -*-

from flask import request
from flask.ext import restful
from flask.ext.restful import reqparse, fields, marshal

from collections import OrderedDict

from geospatial.common.Record import Record

# Argument parser for the GET method. All args are optional
# parser_get = reqparse.RequestParser()
# parser_get.add_argument('decimalLatitude', type=float, location='args')
# parser_get.add_argument('decimalLongitude', type=float, location='args')
# parser_get.add_argument('countryCode', location='args')
# parser_get.add_argument('scientificName', location='args')

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

        # args = parser_get.parse_args()
        args = request.args

        record = Record(args)
        flags = record.parse()

        res = OrderedDict(sorted(args.items(), key=lambda t: t[0]))
        res['flags'] = flags

        return res, 201

    def post(self):

        args = parser_post.parse_args()
        records = args['records']

        for i in range(len(records)):

            record = Record(records[i])
            flags = record.parse()
            res = OrderedDict(sorted(records[i].items(), key=lambda t: t[0]))
            res['flags'] = flags

            records[i] = res

        return records, 201

