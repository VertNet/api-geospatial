import json
from urllib import urlencode

from google.appengine.api import modules, urlfetch
import webapp2

class GeospatialIssue(webapp2.RequestHandler):

    def options(self):
        self.response.headers["Access-Control-Allow-Origin"] = "*"
        self.response.headers["Access-Control-Allow-Headers"] = "content-type"
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write("{}")
        return

    def get(self):

        params = {
            'decimalLatitude': str(self.request.get('decimalLatitude')),
            'decimalLongitude': str(self.request.get('decimalLongitude')),
            'countryCode': str(self.request.get('countryCode')),
            'scientificName': str(self.request.get('scientificName'))
        }

        data = urlencode(params)

        rpc = urlfetch.create_rpc()
        url = "http://"+modules.get_hostname(module="api")+"/geospatial/singlerecord"
        urlfetch.make_fetch_call(
            rpc,
            url=url,
            payload=data,
            method=urlfetch.POST,
            headers={"Content-Type":"application/x-www-form-urlencoded"}
        )
        
        content = rpc.get_result().content.replace("u'", "'").replace("'", '"')

        self.response.headers["Access-Control-Allow-Origin"] = "*"
        self.response.headers["Access-Control-Allow-Headers"] = "content-type"
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(content)
        return


    def post(self):
        
        records = json.loads(self.request.body)
        if type(records) != type([]):
            self.error(400)
            self.response.out.write('{"error":"Must provide a list"}')
            return

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
            rpc = urlfetch.create_rpc()
            params = {
                'decimalLatitude': i[0][0],
                'decimalLongitude': i[0][1],
                'countryCode': i[1],
                'scientificName': i[2]
            }
            data = urlencode(params)
            urlfetch.make_fetch_call(
                rpc,
                url="http://"+modules.get_hostname(module="api")+"/geospatial/singlerecord",
                payload=data,
                method=urlfetch.POST,
                headers={"Content-Type":"application/x-www-form-urlencoded"}
            )
            flags[i]['rpc'] = rpc

        for i in flags.keys():
            flags[i]['flags'] = json.loads(flags[i]['rpc'].get_result().content.replace("u'", "'").replace("'", '"'))['flags']

        # Fill in flags in each record
        for i in idxs.keys():
            records[i]['flags'] = flags[idxs[i]]['flags']

        self.response.headers["Access-Control-Allow-Origin"] = "*"
        self.response.headers["Access-Control-Allow-Headers"] = "content-type"
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(records)
        return