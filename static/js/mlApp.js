'use strict';
var streams = {};
var myApp = angular.module('mlApp', [
    'ngSanitize',
    'ui.router',
    'mgcrea.ngStrap',
    'mlApp.controllers'
])
.config(['$urlRouterProvider', '$stateProvider', function($urlRouterProvider, $stateProvider) {
    $urlRouterProvider.otherwise('/');

    $stateProvider.state('home', {
        url: '/',
        templateUrl: '/partials/home.streams.html',
        resolve: {
            timelines: function($http) {
                return $http.get('/gettimelines');
            }
        },

        controller: function($scope, $state, $rootScope, $modal, $http, timelines) {
            $scope.ml_username = 'paul.shahid';

            var ml_stream = $rootScope.initialFeed;
            streams = {};
            streams['ml_stream'] = {'username': 'SmartTarget Stream'};
            
            //Normalize ML stream data, kinda kludgy
            angular.forEach(ml_stream, function(value, key) {
                value['created_at'] = new Date(value['created_date']).toUTCString().replace(' GMT', '');
                value['idstr'] = value['twitter_id'];
                value['user'] = {name: value['username'], screen_name: value['username']};
                value['text'] = value['message'];
            });

            streams['ml_stream']['statuses'] = ml_stream;
            streams['ml_stream']['name'] = 'SmartConnect Stream';
            streams['ml_stream']['id'] = '-1'; //Assign it -1 for now; back-end needs to know this

            // timelines.data['7620182291'] = {id: '7620182291', name: 'derp', username: 'derp', statuses: []};

            //Normalize the dates of all the other statuses, also kludgy
            angular.forEach(timelines.data, function(value, key) {
                console.log(value);
                angular.forEach(value.statuses, function(status, key) {
                    value.statuses[key].created_at = new Date(status.created_at)
                        .toUTCString()
                        .replace(' GMT', '');
                });
                this[value['username']] = value;
                this[value['username']]['name'] = value['username'];
                this[value['username']]['id'] = key;
            }, streams);

            //Streams is the view-model
            $scope.streams = streams;

            //Root-scope event lets us know when there's an update from the websocket
            $rootScope.$on('ml_feed_update', function(evt, data) {
                console.log("Ml feed update");
                if (!(data.hasOwnProperty('ping'))) {
                    $scope.streams['ml_stream'].statuses.unshift(data);
                } else {
                    console.log("Got ping from other side");
                }
            });

            var modal;

            $scope.reply = function($event, twitterUser, idstr, id) {
                $scope.replyContent = '@' + twitterUser.screen_name;

                //Id of the status to reply to
                $scope.replyId = idstr;

                //Account that's sending the new tweet/reply
                $scope.senderId = id;

                modal = $modal({
                    title: 'Reply to ' + twitterUser.screen_name,
                    show: true,
                    template: 'partials/ReplyTo.html',
                    scope: $scope
                });
            }

            $scope.favorite = function($event, statusId, streamId) {
                $http.post('/favorite', {statusId: statusId, accounts: [streamId]});
            }

            $scope.newStatus = function($event, streamId) {
                $scope.senderId = streamId;
                $scope.newContent = "";
                modal = $modal({
                    show: true,
                    template: 'partials/NewTweet.html',
                    scope: $scope
                });
            }

            $scope.sendReply = function($event, text) {
                modal.hide();

                $http.post('/update', {message: text, reply_id: $scope.replyId, sender: $scope.senderId});

                $scope.senderId = '';
            }

            $scope.sendUpdate = function($event, text) {
                modal.hide();

                $http.post('/update', {message: text, sender: $scope.senderId});
                $scope.senderId = '';
            }

            $scope.acceptable = function($event, id) {
                $rootScope.pushService.acceptable(id);
            }

            $scope.unacceptable = function($event, id) {
                $rootScope.pushService.unacceptable(id);
            }

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

myApp.run(['$rootScope', '$state', 'PushService', function($rootScope, $state, PushService) {

    function broadcastOnActivity(chan, data) {
        var obj = angular.fromJson(data);

        $rootScope.$broadcast('ml_feed_update', obj);
        $state.transitionTo('home');
    }

    PushService.subscribe('feed', broadcastOnActivity);

    $rootScope.initialFeed = null;
    $rootScope.pushService = PushService;

    PushService.getLatestML(
        function(result) {
            console.log("Latest ML acquired");
            var results = angular.fromJson(result);

            $rootScope.initialFeed = results;
        },
        function(error) {
            console.log('Latest ml errback');
            console.log(error);
        }
    );
}]);
