import webapp2

# GEOSPATIAL QUALITY
from geospatial.GeospatialIssue import GeospatialIssue
from geospatial.SingleRecord import SingleRecord

# ... add more imports here

app = webapp2.WSGIApplication([
    
    # GEOSPATIAL QUALITY
    ('/geospatial', GeospatialIssue),
    ('/geospatial/singlerecord', SingleRecord)
    
    # ... add more routes here
], debug=True)