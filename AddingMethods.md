# How to add new methods to the VertNet API

This document tries to explain how to add new methods to the VertNet APIs. It will use the Geospatial Quality method as an example.

## Building the code for the new method

All the method-related code should be in its own folder

```
/
|-- api.yaml
|-- api.py
|-- appengine_config.py
|-- lib/
|-- geospatial/  <---
|------ __init__.py  # Must include this empty fileto enable importing
|------ GeospatialIssue.py
|------ SingleRecord.py
|------ Parser.py
|------ util.py
```

There must be at least one file in the folder that defines the main class for the method. This class must inherit from `webapp2.RequestHandler` and, for the sake of name consistency, should be named as the module itself:

```python
# geospatial/GeospatialIssue.py
import webapp2
...
class GeospatialIssue(webapp2.RequestHandler):
	def get(self):
    	...
```

## Handling third-party dependencies

**IMPORTANT**: Whenever possible, try to avoid external dependencies.

**IMPORTANT**: Before importing external dependencies, make sure they are not already in the lib folder and that they are not incompatible with any of the existing libraries.

If the code needs some external library, make sure to install it via pip and store the files for that library in the `lib` folder:

```bash
pip install -t lib pycountries
```

## Updating `api.py`

There are two steps to effectively link the new method to the APIs, and both involve editing the `api.py` file 

### Import the main class or classes

At the top of the file, add the lines for importing the main class or classes (the ones that inherit from `webapp2.RequestHandler`). Also, if possible, add a comment line to specify which API the imports refer to:

```python
# api.py
...
# GEOSPATIAL QUALITY
from geospatial.GeospatialIssue import GeospatialIssue
from geospatial.SingleRecord import SingleRecord
```

### Add the route to the `WGSIApplication`

At the bottom of the file, add a new pair of elements indicating the route to the API method. The first element of the pair is the endpoint, relative the the base URL (http://api-dev.vertnet-portal.appspot.com) and the second is the name of the main class, as specified in the import. Also, if possible, add a comment line to specify which API the imports refer to:

```python
# api.py
...
app = webapp2.WSGIApplication([
    
    # GEOSPATIAL QUALITY
    ('/geospatial', GeospatialIssue),
    ('/geospatial/singlerecord', SingleRecord)
...
```

## Test and redeploy

Before deploying, launch a local development environment to test the new method **and** to make sure no other method has been damaged. If everything is OK, the APIs are ready to redeploy.