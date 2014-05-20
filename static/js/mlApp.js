'use strict';
var streams = {};
var myApp = angular.module('mlApp', [
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
            $scope.ml_username = ml_username;
            console.log($rootScope.initialFeed);
            var ml_stream = $rootScope.initialFeed;
            streams = {};
            streams['ml_stream'] = {'username': 'ML Stream'};
            
            //Normalize ML stream data, kinda kludgy
            angular.forEach(ml_stream, function(value, key) {
                value['created_at'] = new Date(value['created_date']).toUTCString().replace(' GMT', '');
                value['idstr'] = value['twitter_id'];
                value['user'] = {name: value['username'], screen_name: value['username']};
                value['text'] = value['message'];
            });

            streams['ml_stream']['statuses'] = ml_stream;
            streams['ml_stream']['name'] = 'ML Stream';
            streams['ml_stream']['id'] = '-1'; //Assign it -1 for now; back-end needs to know this

            // timelines.data['7620182291'] = {id: '7620182291', name: 'derp', username: 'derp', statuses: []};

            //Normalize the dates of all the other statuses, also kludgy
            angular.forEach(timelines.data, function(value, key) {
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
    console.log("Running");

    // var wssession;
    // // var wsUrl = 'ws://mlsystems.io/wamp';
    // var wsUrl = 'ws://localhost/wamp';

    // ab.connect(wsUrl, function(session) {
    //     $rootScope.wssession = session;
        
    //     $rootScope.wssession.subscribe('feed', function(chan, data) {
    //         var obj = JSON.parse(data);
    //         obj.created_at = new Date(obj.created_at)
    //             .toUTCString()
    //             .replace(' GMT', '');

    //         $rootScope.$broadcast('ml_feed_update', obj);
    //         $state.transitionTo('home');
    //     });
    // }, function(code, reason,detail) {
    //         console.log("WS connection attempt failed");
    //         console.log(reason);
    // }, {
    //     'maxRetries': 60,
    //     'retryDelay': 2000
    // });
    function broadcastOnActivity(chan, data) {
        var obj = angular.fromJson(data);

        $rootScope.$broadcast('ml_feed_update', obj);
        $state.transitionTo('home');
    }

    PushService.subscribe('feed', broadcastOnActivity);

    $rootScope.initialFeed = null;

    PushService.getLatestML(
        function(result) {
            var results = angular.fromJson(result);

            $rootScope.initialFeed = results;
        },
        function(error) {
            console.log('Latest ml errback');
            console.log(error);
        }
    );
}]);
