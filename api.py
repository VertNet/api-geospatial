import webapp2

# Add API methods
from geospatial.GeospatialIssue import GeospatialIssue
from geospatial.SingleRecord import SingleRecord


app = webapp2.WSGIApplication([
    
    # GEOSPATIAL QUALITY
    ('/geospatial', GeospatialIssue),
    ('/geospatial/singlerecord', SingleRecord)
    
    # ... add more routes here
], debug=True)