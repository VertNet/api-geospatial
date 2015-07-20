'use strict';

// Main application
var geospatialAPI = angular.module('geospatialAPI', [
    'ngResource',
    'geospatialControllers',
    'geospatialServices'
]);

// To avoid confusion between Jinja2 templates and AngularJS expressions
// AngularJS expressions are now like {[{ expr }]}
geospatialAPI.config(['$interpolateProvider', '$locationProvider',
    function($interpolateProvider, $locationProvider) {
        $interpolateProvider.startSymbol('{[{');
        $interpolateProvider.endSymbol('}]}');
        $locationProvider.html5Mode(false).hashPrefix('!');
    }
]);
