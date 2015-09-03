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

class SingleRecord(restful.Resource):
    def post(self):
        values = request.form
        record = Parser(values)
        flags = record.parse()
        res = OrderedDict(sorted(values.items(), key=lambda t: t[0]))
        res['flags'] = flags
        return res