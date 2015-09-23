import json
from urllib import urlencode
from urllib2 import urlopen

from cred import cdb_key

def cdbQuery(q):
    url = 'https://mol.cartodb.com/api/v2/sql'
    params = {
        'q': q,
        'api_key': cdb_key
    }

    data = urlencode(params)
    res = json.loads(urlopen(url, data=data).read())
    return res['rows']
    

def pointRangeDistanceQuery(sciname, lat, lng):
    q = "select rangemap_inside_distance('{0}', {1}, {2})".format(sciname, lat, lng)
    res = cdbQuery(q)

    return res[0]['rangemap_inside_distance']

def pointCountryDistanceQuery(country, lat, lng):
    q = "select ST_Distance(ST_Transform(ST_SetSRID(ST_Point({1}, {0}), 4326), 3857), the_geom_webmercator) as dist from (select the_geom_webmercator from gadm2_country where iso='{2}') as foo;".format(lat, lng, country)
    res = cdbQuery(q)

    return res[0]['dist']