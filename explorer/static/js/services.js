'use strict';

// Service for querying CartoDB
var geospatialServices = angular.module('geospatialServices', ['ngResource']);

geospatialServices.factory ('getRequest', ['$resource',
	function($resource) {
		return $resource('http://'+api_url+'/geospatialissue?decimalLatitude=:lat&decimalLongitude=:lng&countryCode=:cc&scientificName=:sn', {}, {
			get: {method: 'GET', isArray: false}
		});
	}
]);

geospatialServices.factory ('postRequest', ['$resource',
	function($resource) {
		return $resource('http://'+api_url+'/geospatialissue', {}, {
			post: {method: 'POST', isArray: true}
		});
	}
]);