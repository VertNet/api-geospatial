'use strict';

var geospatialControllers = angular.module('geospatialControllers', []);

// Metadata form controller, required to make the mandatory fields be mandatory
geospatialControllers.controller('MainController', ['$scope', '$resource', '$q', 'getRequest',
    function($scope, $resource, $q, getRequest) {
        
        $scope.loading = false;
        $scope.buttonText = "Send!";
        $scope.res = undefined;

        $scope.sendGetRequest = function() {
            $scope.loading = true;
            $scope.res = undefined;
            $scope.buttonText = "Waiting...";

            if ($scope.decimalLatitude || $scope.decimalLongitude || $scope.countryCode || $scope.scientificName) {
                var decimalLatitude = $scope.decimalLatitude;
                var decimalLongitude = $scope.decimalLongitude;
                var countryCode = $scope.countryCode;
                var scientificName = $scope.scientificName;
            } else {
                var decimalLatitude = $scope.decimalLatitude = 42.332;
                var decimalLongitude = $scope.decimalLongitude = -1.833;
                var countryCode = $scope.countryCode = 'ES';
                var scientificName = $scope.scientificName = 'Puma concolor';
            }

            console.log("Sending GET request with these values:");
            console.log("decimalLatitude: " + decimalLatitude);
            console.log("decimalLongitude: " + decimalLongitude);
            console.log("countryCode: " + countryCode);
            console.log("scientificName: " + scientificName);

            var q = $q.defer();
            getRequest.get({lat:decimalLatitude, lng:decimalLongitude, cc:countryCode, sn:scientificName},
                function success(response, headers) {
                    q.resolve("Got response to GET request");
                    console.log("Got response to GET request");
                    $scope.res = response;
                    $scope.head = headers;
                    console.log($scope.res);
                    $scope.loading = false;
                    $scope.buttonText = "Send!";
                },
                function error(errorResponse){
                    q.reject("Error getting dataset title:"+JSON.stringify(errorResponse));
                    $scope.loading = false;
                    $scope.buttonText = "Send!";
                }
            );
        }

        $scope.sendPostRequest = function() {
            console.log("Sending POST request");
        }
    }
]);