var push = angular.module('Push', []);

myApp.service('PushService', ['$q', function($q) {
    ab._Deferred = $q.defer;
    var self = this;

    var websocketUrl = 'ws://' + window.location.host + '/wamp',

        //Array of objects like {action: 'subscribe', params: [params]}
        todoOnConnect = [];
    
    ab.connect(
        websocketUrl,
        connectSuccess,
        connectFailure,
        {
            'maxRetries': 60,
            'retryDelay': 2000
        }
    );
    
    //Autobahn session object
    self.session = null;

    self.connected = false;

    this.subscribe = function(topic, callback) {
        if (isConnected()) {
            self.session.subscribe(topic, callback);
            console.log("Subscribed!");
        } else {
            todoOnConnect.push({'action': 'subscribe', params: [topic, callback]});
        }
    };

    this.unsubscribe = function(topic) {
        if (isConnected()) {
            self.session.unsubscribe(topic);
        } else {
            todoOnConnect.push({'action': 'unsubscribe', params: [topic]});
        }
    };

    //Params must be null or empty array
    this.rpc = function(path, params, callback, errback) {
        if (isConnected()) {
            self.session.call.apply(self.session, [path, params]).then(callback, errback);
        } else {
            var fullParams = [];

            fullParams.push(path);

            if (params && params.length > 0) {
                for(var i=0; i < params.length; i++) {
                    fullParams.push(params[i]);
                }
            }
            todoOnConnect.push({action: 'rpc', params: fullParams, callbacks:[callback, errback]});
        }
    };

    this.publish = function(topic, data) {
        if (isConnected()) {
            self.session.publish(topic, data);
        } else {
            todoOnConnect.push({action: 'publish', params: [data]})
        }
        console.log("Publish!");
    };

    this.getLatestML = function(callback, errback) {
        self.rpc('#getInitMongo', null, callback, errback);
    };

    function connectSuccess(session) {
        console.log("Connected!");

        self.session = session;
        self.connected = true;

        doOnConnect();
    }

    function connectFailure(failure) {
        console.log("Critical failure");
        console.log(failure);

        self.connected = false;
    }

    function doOnConnect() {
        var actionDispatch = {
            'subscribe': self.subscribe,
            'unsubscribe': self.unsubscribe,
            'rpc': self.rpc,
            'publish': self.publish
        };

        angular.forEach(todoOnConnect, function(value, key) {

            if (actionDispatch.hasOwnProperty(value.action) && value.action !== 'rpc') {
                actionDispatch[value.action].apply(self, value.params);

            } else if (value.action === 'rpc') {
                //We expect this value object to look like {action: 'rpc', params: [], callbacks: [success, failure]}
                self.session.call.apply(
                    self.session,
                    value.params
                ).then(value.callbacks[0], value.callbacks[1]);
                console.log('Did the RPC thing');
            }

        });

        //Flush the array after all functions have been called
        todoOnConnect = new Array();
    }

    function isConnected() {
        return self.session !== null && self.connected;
    }
}]);