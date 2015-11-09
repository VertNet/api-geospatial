'use strict';

// Main application
var geospatialAPI = angular.module('geospatialAPI', [
    'ngResource',
    'geospatialControllers',
    'geospatialServices'
]);

// To avoid confusion between Jinja2 templates and AngularJS expressions
// AngularJS expressions are now like {[{ expr }]}
geospatialAPI.config(['$interpolateProvider', '$locationProvider', '$httpProvider',
    function($interpolateProvider, $locationProvider, $httpProvider) {
        $interpolateProvider.startSymbol('{[{');
        $interpolateProvider.endSymbol('}]}');
        $locationProvider.html5Mode(false).hashPrefix('!');
        $httpProvider.defaults.useXDomain = true;
    	delete $httpProvider.defaults.headers.common['X-Requested-With'];
    }
]);
