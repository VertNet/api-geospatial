import requests

from cred import cdb_key

def cdbQuery(q):
    url = 'https://mol.cartodb.com/api/v2/sql'
    params = {
        'q': q,
        'api_key': cdb_key
    }
    
    r = requests.get(url, params=params)
    
    return r.json()['rows']
