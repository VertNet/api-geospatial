# -*- coding: utf-8 -*-

from flask import request, make_response
from flask.ext import restful
from flask.ext.restful import reqparse, fields, marshal

from collections import OrderedDict
from datetime import datetime
import logging
import json

#from google.appengine.api import taskqueue
from google.appengine.api import taskqueue, modules

from geospatial.common.Parser import Parser

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

    def parse_record(self, values):
        record = Parser(values)
        flags = record.parse()
        res = OrderedDict(sorted(values.items(), key=lambda t: t[0]))
        res['flags'] = flags
        return res


    def get(self):
        # args = parser_get.parse_args()
        args = request.args
        
        res = self.parse_record(args)

        response = make_response(json.dumps(res))
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Content-Type"] = "application/json"
        return response

    def post(self):
        ini = datetime.now()
        args = parser_post.parse_args()
        records = args['records']
        
        idxs = {}
        flags = {}

        # Extract indices for records
        for i in range(len(records)):
            decimalLatitude = records[i]['decimalLatitude'] if 'decimalLatitude' in records[i].keys() else None
            decimalLongitude = records[i]['decimalLongitude'] if 'decimalLongitude' in records[i].keys() else None
            countryCode = records[i]['countryCode'] if 'countryCode' in records[i].keys() else None
            scientificName = records[i]['scientificName'] if 'scientificName' in records[i].keys() else None
            idx = ((decimalLatitude, decimalLongitude), countryCode, scientificName)
            idxs[i] = idx
            flags[idx] = {}

        for i in flags.keys():
            values = {
                'decimalLatitude': i[0][0],
                'decimalLongitude': i[0][1],
                'countryCode': i[1],
                'scientificName': i[2]
            }
            flags[i]['flags'] = self.parse_record(values)['flags']

        # Fill in flags in each record
        for i in idxs.keys():
            res = OrderedDict(sorted(records[i].items(), key=lambda t: t[0]))
            res['flags'] = flags[idxs[i]]['flags']
            records[i] = res

        end = datetime.now()
        logging.info("API functions called {0} times".format(len(flags.keys())))
        logging.info("Elapsed: {0}".format(end-ini))
        
        response = make_response(json.dumps(records))
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "content-type"
        response.headers["Content-Type"] = "application/json"
        return response

    def options(self):
        """Dummy method to avoid CORS issues when calling from AngularJS."""
        response = make_response(json.dumps('{}'))
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "content-type"
        response.headers["Content-Type"] = "application/json"
        return response
