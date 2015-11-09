import webapp2

from geospatial.Parser import Parser

class SingleRecord(webapp2.RequestHandler):
    def post(self):
        
        # values = self.request.arguments()
        values = {
            'decimalLatitude': self.request.get('decimalLatitude'),
            'decimalLongitude': self.request.get('decimalLongitude'),
            'countryCode': self.request.get('countryCode'),
            'scientificName': self.request.get('scientificName')
        }
        record = Parser(values)
        flags = record.parse()
        #res = OrderedDict(sorted(values.items(), key=lambda t: t[0]))
        res = values
        res['flags'] = flags

        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers["Access-Control-Allow-Origin"] = "*"
        self.response.write(flags)