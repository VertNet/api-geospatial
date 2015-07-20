'use strict';

// Service for querying CartoDB
var geospatialServices = angular.module('geospatialServices', ['ngResource']);

geospatialServices.factory ('getRequest', ['$resource',
	function($resource) {
		return $resource('http://localhost:8080/geospatialissue?decimalLatitude=:lat&decimalLongitude=:lng&countryCode=:cc&scientificName=:sn', {}, {
			get: {method: 'GET', isArray: false}
		});
	}
]);