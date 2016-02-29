import ast
import json
import logging
from urllib import urlencode
from util import chunks

from google.appengine.api import modules, urlfetch
from google.appengine.runtime import DeadlineExceededError
import webapp2

MODULE = modules.get_current_module_name()
URLFETCH_DEADLINE = 60
POST_CHUNK_SIZE = 100

class GeospatialIssue(webapp2.RequestHandler):

    def options(self):
        self.response.headers["Access-Control-Allow-Origin"] = "*"
        self.response.headers["Access-Control-Allow-Headers"] = "content-type"
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write("{}")
        return

    def get(self):

        params = {
            'decimalLatitude': self.request.get('decimalLatitude'),
            'decimalLongitude': self.request.get('decimalLongitude'),
            'countryCode': self.request.get('countryCode'),
            'scientificName': self.request.get('scientificName')
        }

        # Try to cast coords to floats, keep strings if error
        try:
            params['decimalLatitude'] = round(float(params['decimalLatitude']), len(params['decimalLatitude'].split(".")[1]))
        except ValueError:
            pass
        try:
            params['decimalLongitude'] = round(float(params['decimalLongitude']), len(params['decimalLongitude'].split(".")[1]))
        except ValueError:
            pass

        data = urlencode(params)

        urlfetch.set_default_fetch_deadline(URLFETCH_DEADLINE)

        url = "http://"+modules.get_hostname(module=MODULE)+"/geospatial/singlerecord"
        result = urlfetch.fetch(
            url=url,
            payload=data,
            method=urlfetch.POST,
            headers={"Content-Type":"application/x-www-form-urlencoded"}
        )

        fl = ast.literal_eval(result.content)
        params['flags'] = fl

        self.response.headers["Access-Control-Allow-Origin"] = "*"
        self.response.headers["Access-Control-Allow-Headers"] = "content-type"
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(params))
        return


    def post(self):
        
        urlfetch.set_default_fetch_deadline(URLFETCH_DEADLINE)

        try:
            records = json.loads(self.request.body)
            logging.info(len(records))

        except ValueError:
            self.error(400)
            self.response.out.write('{"error":"Wrong input format. Must provide a list-type object with the records"}')
            return
        if self.request.body == '' or type(records) != type([]):
            self.error(400)
            self.response.out.write('{"error":"Wrong input format. Must provide a list-type object with the records"}')
            return
        if len(records) > 1000:
            self.error(400)
            self.response.out.write('{"error":"Too many records. There is a hard limit of 1000 records per request"}')
            return

        idxs = {}
        flags = {}

        # Extract indices for records
        for i in range(len(records)):

            # Get values from record
            decimalLatitude = records[i]['decimalLatitude'] if 'decimalLatitude' in records[i].keys() else None
            decimalLongitude = records[i]['decimalLongitude'] if 'decimalLongitude' in records[i].keys() else None
            countryCode = records[i]['countryCode'] if 'countryCode' in records[i].keys() else None
            scientificName = records[i]['scientificName'] if 'scientificName' in records[i].keys() else None

            # Try to cast coords to floats, keep strings if error
            try:
                decimalLatitude = round(float(decimalLatitude), len(decimalLatitude.split(".")[1]))
            except ValueError:
                pass
            try:
                decimalLongitude = round(float(decimalLongitude), len(decimalLongitude.split(".")[1]))
            except ValueError:
                pass
            
            # Build "ID" by tupling values
            idx = ((decimalLatitude, decimalLongitude), countryCode, scientificName)

            # Store id in position in array
            idxs[i] = idx

            # Initialize empty flag object for that ID
            flags[idx] = {}

        # ADDED TO AVOID query_wait_timeout ISSUES IN CARTODB

        # Divide list of IDs into smaller chunks
        idx_chunks = chunks(flags.keys(), POST_CHUNK_SIZE)

        # Process chunks iteratively
        for chunk in idx_chunks:

            logging.info("Processing chunk of %d IDs" % len(chunk))

            # Create and launch RPCs
            for i in chunk:

                # Create a new RPC
                rpc = urlfetch.create_rpc()
                params = {
                    'decimalLatitude': i[0][0],
                    'decimalLongitude': i[0][1],
                    'countryCode': i[1],
                    'scientificName': i[2]
                }
                try:
                    data = urlencode(params)
                except UnicodeEncodeError:
                    logging.error(params)
                    raise UnicodeEncodeError
                
                # Launch the async call to singlerecord
                urlfetch.make_fetch_call(
                    rpc,
                    url="http://"+modules.get_hostname(module=MODULE)+"/geospatial/singlerecord",
                    payload=data,
                    method=urlfetch.POST,
                    headers={"Content-Type":"application/x-www-form-urlencoded"}
                )

                # Store the rpc
                flags[i]['rpc'] = rpc

            # Wait for RPCs to finish and get results
            for i in chunk:

                result = flags[i]['rpc'].get_result()
                fl = ast.literal_eval(result.content)
                flags[i]['flags'] = fl
                # try:
                #     result = flags[i]['rpc'].get_result()
                # except QueryWaitTimeoutError:
                #     logging.warning("Got query_wait_timeout error, retrying")
                # flags[i]['flags'] = json.loads(flags[i]['rpc'].get_result().content.replace("u'", "'").replace("'", '"'))['flags']

        # Fill in flags in each record
        for i in idxs.keys():
            records[i]['flags'] = flags[idxs[i]]['flags']

        self.response.headers["Access-Control-Allow-Origin"] = "*"
        self.response.headers["Access-Control-Allow-Headers"] = "content-type"
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(records))

        return