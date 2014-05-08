'use strict';
var streams = {};
var myApp = angular.module('mlApp', [
    'ui.router',
    'mlApp.controllers'
])
.config(['$urlRouterProvider', '$stateProvider', function($urlRouterProvider, $stateProvider) {
    $urlRouterProvider.otherwise('/');

    $stateProvider.state('home', {
        url: '/',
        templateUrl: '/partials/home.streams.html',
        resolve: {
            ml_stream: function($q, $rootScope, $http, $timeout) {

                var deferred = $q.defer();
  
                $timeout(function() {
                    var date;

                    if (typeof date === "undefined" || date === null) {
                        date = new Date().toISOString();
                    }

                    $rootScope.wssession.call('#getInit', date).then(
                        function(result) {
                            var results = [];
                            console.log("Got initial results");
                            angular.forEach(result, function(value, key) {

                                this.push(JSON.parse(value.replace(/'/g, '"')));
                            
                            }, results);

                            deferred.resolve(results);
                            console.log("Returning initial results");
                            $rootScope.$apply();
                        },
                        function(error) {
                            console.log(error);
                            deferred.reject(error);
                            $rootScope.$apply();
                        }
                    );
                }, 1000);
                return deferred.promise;
            },
            timelines: function($http) {
                return $http.get('/gettimelines');
            }
        },

        controller: function($scope, $state, $rootScope, ml_stream, timelines) {
            // $scope.streams = [{name: 'ML Stream', id: 'ml-stream'}];
            console.log("Doing the thing");
            $scope.accounts = ['dev_shahid', 'lockwoodgame', 'derp'];
            streams = {};
            streams['ml_stream'] = {'username': 'ML Stream'};
            
            angular.forEach(ml_stream, function(value, key) {
                value['created_at'] = value['created_date'];
                value['idstr'] = value['twitter_id'];
                value['user'] = {name: value['username'], screen_name: value['username']};
                value['text'] = value['message'];
            });

            streams['ml_stream']['statuses'] = ml_stream;
            streams['ml_stream']['name'] = 'ML Stream';

            // timelines.data['7620182291'] = {id: '7620182291', name: 'derp', username: 'derp', statuses: []};
            
            angular.forEach(timelines.data, function(value, key) {
                this[value['username']] = value;
                this[value['username']]['name'] = value['username'];
                this[value['username']]['id'] = key;
            }, streams);

            $scope.streams = streams;
            $rootScope.$on('ml_feed_update', function(evt, data) {

                if (!(data.hasOwnProperty('ping'))) {
                    $scope.streams['ml_stream'].statuses.unshift(data);
                }
            });
        }
    });

    $stateProvider.state('about', {
        url: '/about',
        templateUrl: '/partials/about.html'
    });

    $stateProvider.state('contact', {
        url: '/contact',
        template: ''
    });
}]);

myApp.run(['$rootScope', '$state', function($rootScope, $state) {
    console.log("Running");

    var wssession;
    var wsUrl = 'ws://localhost:9001/wamp';

    ab.connect(wsUrl, function(session) {
        $rootScope.wssession = session;
        
        $rootScope.wssession.subscribe('feed', function(chan, data) {
            console.log(data);
            $rootScope.$broadcast('ml_feed_update', JSON.parse(data));
            $state.transitionTo('home');
        });
    }, function(code, reason,detail) {
            console.log("WS connection attempt failed");
            console.log(reason);
    }, {
        'maxRetries': 60,
        'retryDelay': 2000
    });

}]);