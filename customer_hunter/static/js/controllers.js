'use strict';

angular.module('mlApp.controllers', [])
	.controller('NavController', ['$scope', function($scope) {
		$scope.name = 'paul.shahid'
		$scope.template = '/partials/nav.html';
	}]);