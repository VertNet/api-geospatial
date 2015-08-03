# -*- coding: utf-8 -*-

from flask import request
from flask.ext import restful
from flask.ext.restful import reqparse, fields, marshal

from collections import OrderedDict
from datetime import datetime
import logging

from google.appengine.api import taskqueue
from google.appengine.api import urlfetch

from geospatial.common.Parser import Parser

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

        record = Parser(args)
        flags = record.parse()

        res = OrderedDict(sorted(args.items(), key=lambda t: t[0]))
        res['flags'] = flags

        return res, 200

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

        # Calculate flags for each index
        for i in flags.keys():
            record = Parser({
                'decimalLatitude': i[0][0],
                'decimalLongitude': i[0][1],
                'countryCode': i[1],
                'scientificName': i[2]
            })
            flags[i] = record.parse()

        # Fill in flags in each record
        for i in idxs.keys():
            res = OrderedDict(sorted(records[i].items(), key=lambda t: t[0]))
            res['flags'] = flags[idxs[i]]
            records[i] = res


            # record = Parser(records[i])
            # flags = record.parse()
            # res = OrderedDict(sorted(records[i].items(), key=lambda t: t[0]))
            # res['flags'] = flags

            # records[i] = res

        end = datetime.now()
        logging.info("API functions called {0} times".format(len(flags.keys())))
        logging.info("Elapsed: {0}".format(end-ini))
        return records, 200

