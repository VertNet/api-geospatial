import json
import logging
from collections import OrderedDict
from urllib2 import urlopen
from urllib import urlencode

from google.appengine.api import memcache

from pycountry import countries
from geospatial.common.util import pointRangeDistanceQuery, pointCountryDistanceQuery

gn_api = "http://api.geonames.org/"

class Record():
    def __init__(self, record):
        self.username = "jotegui"
        self.raw = record
        self.occurrenceId = self.raw['occurrenceId'] if 'occurrenceId' in self.raw else None
        self.flags = OrderedDict()
        
        return

    def parse(self):
        
        # Completeness
        self.hasCoordinates()
        self.hasCountry()
        self.hasScientificName()

        # Validity
        if self.flags['hasCoordinates'] is True:
            self.validCoordinates()

        if self.flags['hasCountry'] is True:
            self.validCountry()

        if self.flags['hasScientificName'] is True:
            self.validScientificName()
        
        # Common errors
        if 'validCoordinates' in self.flags and self.flags['validCoordinates'] is True:
            self.nonZeroCoordinates()
            self.highPrecisionCoordinates()

            # Geospatial issues
            if 'validCountry' in self.flags and self.flags['validCountry'] is True:
                
                # Check if cached
                # Coordinates rounded to 3 decimal places (111m)
                memcache_key = '|'.join([str(round(self.decimalLatitude, 3)), str(round(self.decimalLongitude, 3)), str(self.countryCode), 'geosp'])
                cached = memcache.get(memcache_key)
                if cached is not None:
                    logging.info("Retrieved from memcache: {}".format(memcache_key))
                    self.geoflags = cached
                else:

                    self.geoflags = OrderedDict()
                    # No transformation
                    inside = self.coordinatesInsideCountry()
                    if inside is False:
                        # Lat negation
                        inside = self.negatedLatitudeInsideCountry()
                        if inside is False:
                            # Lng negation
                            inside = self.negatedLongitudeInsideCountry()
                            if inside is False:
                                # LatLng negation
                                inside = self.negatedCoordinatesInsideCountry()
                                if inside is False:
                                    # Transposition
                                    inside = self.transposedInsideCountry()
                                    if inside is False:
                                        # T + Lat negation
                                        inside = self.tNegatedLatitudeInsideCountry()
                                        if inside is False:
                                            # T + Lng negation
                                            inside = self.tNegatedLongitudeInsideCountry()
                                            if inside is False:
                                                # T + LatLng negation
                                                inside = self.tNegatedCoordinatesInsideCountry()
                                                if inside is False:
                                                    # Nothing works
                                                    self.distanceToCountry()

                    if not memcache.set(memcache_key, self.geoflags):
                        logging.error('Memcache set failed for geoflags.')

                for i in self.geoflags:
                    self.flags[i] = self.geoflags[i]

            # Spatio-taxonomic issues
            if self.flags['hasScientificName'] is True: self.flags['validScientificName'] = True  # TODO: REMOVE WHEN validScientificName IS IMPLEMENTED
            if 'validScientificName' in self.flags and self.flags['validScientificName'] is True:
                self.flags.pop('validScientificName', None)  # TODO: REMOVE WHEN validScientificName IS IMPLEMENTED

                # Check if cached
                # Coordinates rounded to 3 decimal places (111m)
                memcache_key = '|'.join([str(round(self.decimalLatitude, 3)), str(round(self.decimalLongitude, 3)), str(self.scientificName), 'range'])
                cached = memcache.get(memcache_key)
                if cached is not None:
                    logging.info("Retrieved from memcache: {}".format(memcache_key))
                    self.rangeflags = cached
                else:

                    # No transformations, just plain distance
                    self.rangeflags = self.pointRangeDistance()

                    if not memcache.set(memcache_key, self.rangeflags):
                        logging.error('Memcache set failed for rangeflags.')

                for i in self.rangeflags:
                    self.flags[i] = self.rangeflags[i]


        return self.flags

    

    # COMPLETENESS

    def hasCoordinates(self):
        """Coordinate completion. Returns True if both decimalLatitude and decimalLongitude are present and have a value, False otherwise."""
        if 'decimalLatitude' in self.raw and 'decimalLongitude' in self.raw and self.raw['decimalLatitude']!="" and self.raw['decimalLatitude'] is not None and self.raw['decimalLongitude']!="" and self.raw['decimalLongitude'] is not None:
            self.decimalLatitude = self.raw['decimalLatitude']
            self.decimalLongitude = self.raw['decimalLongitude']
            self.flags['hasCoordinates'] = True
        else:
            self.flags['hasCoordinates'] = False
        return

    def hasCountry(self):
        """Country field completion. Returns True if countryCode is present and has a value, False otherwise."""
        if 'countryCode' in self.raw and self.raw['countryCode']!="" and self.raw['countryCode'] is not None:
            self.countryCode = self.raw['countryCode']
            self.flags['hasCountry'] = True
        else:
            self.flags['hasCountry'] = False
        return

    def hasScientificName(self):
        """Scientific name field completion. Returns True if scientificName is present and has a value, False otherwise."""
        if 'scientificName' in self.raw and self.raw['scientificName']!="" and self.raw['scientificName'] is not None:
            self.scientificName = self.raw['scientificName']
            self.flags['hasScientificName'] = True
        else:
            self.flags['hasScientificName'] = False
        return

    

    # VALIDITY

    def validCoordinates(self):
        """Coordinate validation. Returns True if coordinates are numeric and within natural boundaries, False otherwise."""
        # if type(self.decimalLatitude) == type(u"a") or type(self.decimalLongitude) == type(u"a"):
        #     self.flags['validCoordinates'] = False
        # else:
        try:
            if abs(float(self.decimalLatitude))>90 or abs(float(self.decimalLongitude))>180:
                self.flags['validCoordinates'] = False
            else:
                self.decimalLatitude = float(self.decimalLatitude)
                self.decimalLongitude = float(self.decimalLongitude)
                self.flags['validCoordinates'] = True
        except ValueError:
            self.flags['validCoordinates'] = False
        except TypeError:
            self.flags['validCoordinates'] = False
        return

    def validCountry(self):
        """Country validation. Returns True if country code represents an actual country, False otherwise."""
        try:
            countries.get(alpha2=self.countryCode)
            self.flags['validCountry'] = True
        except KeyError:
            self.flags['validCountry'] = False
        return


    def validScientificName(self):
        # TODO
        return

    

    # COMMON ISSUES

    def nonZeroCoordinates(self):
        """Check if both coordinates are 0."""
        if self.decimalLatitude==0 and self.decimalLongitude==0:
            self.flags['nonZeroCoordinates'] = False
        else:
            self.flags['nonZeroCoordinates'] = True
        return

    def highPrecisionCoordinates(self):
        """Check if coordinates have two or less decimal figures."""
        latlen = len(str(float(self.decimalLatitude)).split('.')[1])
        lnglen = len(str(float(self.decimalLongitude)).split('.')[1])
        if latlen<=2 or lnglen<=2:
            self.flags['highPrecisionCoordinates'] = False
        else:
            self.flags['highPrecisionCoordinates'] = True
        return



    # BASE POINT-IN-COUNTRY AND POINT-IN-RANGE CHECKS

    def pointInCountry(self, lat="", lng="", ccode="", radius=""):
        """Check if given point falls within given country."""
        params = {
            "lat": lat,
            "lng": lng,
            "radius": radius,
            "username": self.username
        }

        url = gn_api+"countryCode"
        data = urlencode(params)
        res = urlopen(url, data=data).read()
        if res.rstrip() == ccode:
            return True
        else:
            return False


    # GEOSPATIAL ASSESSMENTS

    def coordinatesInsideCountry(self):
        """Check if original coordinates fall inside specified country."""
        inside = self.pointInCountry(self.decimalLatitude, self.decimalLongitude, self.countryCode)
        self.geoflags['coordinatesInsideCountry'] = inside
        # if inside is True:
        #     self.geoflags['negatedLatitude'] = False
        #     self.geoflags['negatedLongitude'] = False
        #     self.geoflags['transposedCoordinates'] = False
        return inside

    def negatedLatitudeInsideCountry(self):
        """Check if coordinates with negated latitude fall inside specified country."""
        inside = self.pointInCountry(-1*self.decimalLatitude, self.decimalLongitude, self.countryCode)
        if inside is True:
            self.geoflags['negatedLatitude'] = True
            self.geoflags['negatedLongitude'] = False
            self.geoflags['transposedCoordinates'] = False
        return inside

    def negatedLongitudeInsideCountry(self):
        """Check if coordinates with negated longitude fall inside specified country."""
        inside = self.pointInCountry(self.decimalLatitude, -1*self.decimalLongitude, self.countryCode)
        if inside is True:
            self.geoflags['negatedLatitude'] = False
            self.geoflags['negatedLongitude'] = True
            self.geoflags['transposedCoordinates'] = False
        return inside

    def negatedCoordinatesInsideCountry(self):
        """Check if coordinates with both values negated fall inside specified country."""
        inside = self.pointInCountry(-1*self.decimalLatitude, -1*self.decimalLongitude, self.countryCode)
        if inside is True:
            self.geoflags['negatedLatitude'] = True
            self.geoflags['negatedLongitude'] = True
            self.geoflags['transposedCoordinates'] = False
        return inside

    def transposedInsideCountry(self):
        """Check if transposed coordinates fall inside specified country."""
        inside = self.pointInCountry(self.decimalLongitude, self.decimalLatitude, self.countryCode)
        if inside is True:
            self.geoflags['negatedLatitude'] = False
            self.geoflags['negatedLongitude'] = False
            self.geoflags['transposedCoordinates'] = True
        return inside

    
    def tNegatedLatitudeInsideCountry(self):
        """Check if transposed coordinates with negated latitude fall inside specified country."""
        inside = self.pointInCountry(-1*self.decimalLongitude, self.decimalLatitude, self.countryCode)
        if inside is True:
            self.geoflags['negatedLatitude'] = True
            self.geoflags['negatedLongitude'] = False
            self.geoflags['transposedCoordinates'] = True
        return inside

    def tNegatedLongitudeInsideCountry(self):
        """Check if transposed coordinates with negated longitude fall inside specified country."""
        inside = self.pointInCountry(self.decimalLongitude, -1*self.decimalLatitude, self.countryCode)
        if inside is True:
            self.geoflags['negatedLatitude'] = False
            self.geoflags['negatedLongitude'] = True
            self.geoflags['transposedCoordinates'] = True
        return inside

    def tNegatedCoordinatesInsideCountry(self):
        """Check if transposed coordinates with both values negated fall inside specified country."""
        inside = self.pointInCountry(-1*self.decimalLongitude, -1*self.decimalLatitude, self.countryCode)
        if inside is True:
            self.geoflags['negatedLatitude'] = True
            self.geoflags['negatedLongitude'] = True
            self.geoflags['transposedCoordinates'] = True
        return inside

    def distanceToCountry(self):
        """Calculate smallest distance between coordinates and specified country."""
        self.geoflags['negatedLatitude'] = False
        self.geoflags['negatedLongitude'] = False
        self.geoflags['transposedCoordinates'] = False
        
        country3 = countries.get(alpha2=self.countryCode).alpha3
        dist = pointCountryDistanceQuery(country3, self.decimalLatitude, self.decimalLongitude)
        if dist is not None:
            self.geoflags['distanceToCountryInKm'] = round(dist/1000, 3)
        return


    # SPATIO-TAXONOMIC ASSESSMENTS

    def pointRangeDistance(self):
        """Check if original coordinates fall inside range map of specified species and calculate distance if not."""
        rangeflags = OrderedDict()
        dist = pointRangeDistanceQuery(self.scientificName, self.decimalLatitude, self.decimalLongitude)
        if dist is not None:
            if dist == 0:
                rangeflags['coordinatesInsideRangeMap'] = True
                rangeflags['distanceToRangeMapInKm'] = 0
            else:
                rangeflags['coordinatesInsideRangeMap'] = False
                rangeflags['distanceToRangeMapInKm'] = round(dist/1000, 3)

        return rangeflags