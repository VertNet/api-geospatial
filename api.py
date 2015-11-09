import webapp2

# GEOSPATIAL QUALITY
from geospatial.GeospatialIssue import GeospatialIssue
from geospatial.SingleRecord import SingleRecord
from geospatial.Explorer import GeospatialExplorerHandler

# ... add more imports here

app = webapp2.WSGIApplication([
    
    # GEOSPATIAL QUALITY
    ('/geospatial', GeospatialIssue),
    ('/geospatial/singlerecord', SingleRecord),
    ('/explorer/geospatial', GeospatialExplorerHandler)
    
    # ... add more routes here
], debug=True)