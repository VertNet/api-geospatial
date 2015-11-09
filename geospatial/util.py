import time
import json
from urllib import urlencode
# from urllib2 import urlopen
from google.appengine.api import urlfetch
import logging

from cred import cdb_key

URLFETCH_DEADLINE = 60


class QueryWaitTimeoutError(Exception):
    pass


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


# def safeGetResult(rpc):
#     while True:
#         try:
#             result = rpc.get_result()
#             return result
#         except QueryWaitTimeoutError:
#             logging.warning("Got query_wait_timeout error, retrying")


def cdbQuery(q):
    url = 'https://mol.cartodb.com/api/v2/sql'
    params = {
        'q': q,
        'api_key': cdb_key
    }

    data = urlencode(params)
    # res = json.loads(urlopen(url, data=data).read())
    urlfetch.set_default_fetch_deadline(URLFETCH_DEADLINE)

    while True:
        res = json.loads(urlfetch.fetch(url=url, payload=data, method=urlfetch.POST).content)

        if 'error' in res:
            if res['error'][0] == 'query_wait_timeout':
                logging.warning("Got query_wait_timeout error, retrying")
                time.sleep(3)
            else:
                logging.error("Error while calling CartoDB with data %s, gave result %s" % (data, res))
                raise KeyError
                break
        elif 'rows' in res:
            return res['rows']
        else:
            logging.error("Something bad happened when calling CartoDB with data %s, gave result %s" % (data, res))
            raise KeyError
            break


def pointRangeDistanceQuery(sciname, lat, lng):
    q = "select rangemap_inside_distance('{0}', {1}, {2})".format(sciname, lat, lng)
    res = cdbQuery(q)

    return res[0]['rangemap_inside_distance']


def pointCountryDistanceQuery(country, lat, lng):
    q = "select ST_Distance(ST_Transform(ST_SetSRID(ST_Point({1}, {0}), 4326), 3857), the_geom_webmercator) as dist from (select the_geom_webmercator from gadm2_country where iso='{2}') as foo;".format(lat, lng, country)
    res = cdbQuery(q)

    return res[0]['dist']