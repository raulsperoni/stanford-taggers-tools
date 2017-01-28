'use strict';



// Declare app level module which depends on views, and components
angular.module('krypton', [
        'satellizer',
        'ngResource',
        'ngRoute',
        'ngProgress',
    'ui-notification',
        'ui.bootstrap'])
    .constant('baseDataUrl', "http://localhost:8889/ner/api/")
    //.constant('baseDataUrl', "http://192.168.99.100:8889/ner/api/")
    //.constant('baseDataUrl', "https://krypton.mgcoders.uy/ner/api/")



    .factory('InfoFactory', function ($resource, baseDataUrl) {
        return $resource(baseDataUrl + 'info/');
    })

    .factory('TweetFactory', function ($resource, baseDataUrl) {
        return $resource(baseDataUrl + 'tweet/unclassified/');
    })

    .factory('CassifyFactory', function ($resource, baseDataUrl) {
        return $resource(baseDataUrl + 'tweet/classify', {}, {
            save: {
                method: 'POST',
                cache: false,
                isArray: false,
                headers: {'Content-Type': 'application/json; charset=UTF-8'}
            }
        })
    })

    .controller('AppCtrl', ['$scope', 'TweetFactory', 'ngProgressFactory', 'CassifyFactory', '$route', '$location', 'Notification','$timeout', 'InfoFactory', function ($scope, TweetFactory, ngProgressFactory, CassifyFactory, $route, $location, Notification, $timeout,InfoFactory) {

        $scope.progressbar = ngProgressFactory.createInstance();

        $scope.clases = ['PERS', 'LUG', 'ORG', 'OTROS', 'Ninguna'];


        $scope.loadWidget = function () {
            $timeout(function() {
                if(angular.element(document.querySelector('post_' + $scope.tweetid)).find('iframe').length === 0) {
                    twttr.widgets.createTweet($scope.tweetid, document.getElementById('post_' + $scope.tweetid)).then(function(resp) {
                        $timeout(function() {
                            $scope.loading = false;
                        })
                    });
                };
            }, 100);
        };

        $scope.eraseWidget = function(){
            document.getElementById('post_' + $scope.tweetid).innerHTML = '<div  id="{{\'post_\' + tweetid}}"></div>';
        };

        $scope.cargarTweet = function () {
            TweetFactory.get({}).$promise.then(function (data) {
                $scope.tweet = data;
                if ($scope.tweet.error) {
                    $scope.progressbar.complete();
                    $scope.loading = false;
                    $scope.success = false;
                } else {
                    for (var idx in $scope.tweet.ner_entities) {
                        var par = $scope.tweet.ner_entities[idx];
                        if (par.class != 'Ninguna') {
                            $scope.entidades[par.pos] = par;
                        } else {
                            $scope.no_entidades[par.pos] = par;
                        }
                    }
                    $scope.tweetid = $scope.tweet.origin_id;
                    $scope.loadWidget();
                    $scope.progressbar.complete();
                    $scope.loading = false;
                    $scope.success = true;
                }
            });
        };

        $scope.cargarInfo = function () {
            InfoFactory.get({}).$promise.then(function (data) {
                $scope.info = data;
            });
        }

        $scope.seleccionarClase = function (label, par) {
            if (label != 'Ninguna') {
                delete $scope.no_entidades[par.pos];
                par.class = label;
                $scope.entidades[par.pos] = par;
            } else {
                delete $scope.entidades[par.pos];
                par.class = label;
                $scope.no_entidades[par.pos] = par;
            }
            console.info($scope.entidades);
            console.info($scope.no_entidades);
            Notification({message:'Nueva clase para ' + par.entity + ' : ' + par.class, positionY: 'bottom', positionX: 'right'});
        };

        $scope.reloadRoute = function () {
            $location.path("/tweets");
        };

        $scope.enviarTodo = function () {
            CassifyFactory.save($scope.tweet)
                .$promise.then(function (data) {
                Notification({message:'Clasificado, gracias!', positionY: 'bottom', positionX: 'right'});
                $scope.eraseWidget();
                $scope.cargaInicio();
                $scope.cargarTweet();
                $scope.cargarInfo();
            }).catch(function(fallback) {
                Notification.error({message: fallback, delay: 1000, positionY: 'bottom', positionX: 'right'})
            });
        };

        $scope.hayModificaciones = function () {
            for (var idx in $scope.tweet.ner_entities) {
                var par = $scope.tweet.ner_entities[idx];
                if ($scope.entidades[par.pos]!=null) {
                    $scope.tweet.ner_entities[idx] = $scope.entidades[par.pos];
                } else if ($scope.no_entidades[par.pos]!=null) {
                    $scope.tweet.ner_entities[idx] = $scope.no_entidades[par.pos];
                } else {
                    alert("ERROR");
                }
            }
            $scope.enviarTodo();
        };

        $scope.noClasificar = function () {
            $scope.eraseWidget();
            $scope.cargaInicio();
            $scope.cargarTweet();
            $scope.cargarInfo();
        };

        $scope.cargaInicio = function () {
            $scope.progressbar.start();
            $scope.loading = true;
            $scope.success = false;
            $scope.isCollapsed = true;
            $scope.isCollapsedInstrucciones = true;
            $scope.entidades = {}
            $scope.no_entidades = {}
            $scope.info = {}
            $scope.tweetid = undefined;
        };

        //Showtime
        $scope.cargaInicio();
        $scope.cargarTweet();
        $scope.cargarInfo();

    }])

    .controller('LoginCtrl', ['$scope','$auth','$location','Notification', function($scope, $auth, $location,Notification) {

        $scope.email = null;
        $scope.password = null;
        $scope.login = function(){
            $auth.login({
                email: $scope.email,
                password: $scope.password
                })
                .then(function(){
                    // Si se ha logueado correctamente, lo tratamos aquí.
                    // Podemos también redirigirle a una ruta
                    $location.path("/tweets");
                })
                .catch(function(response){
                    // Si ha habido errores llegamos a esta parte
                    Notification.error({message: response.data.message, delay: 1000, positionY: 'bottom', positionX: 'right'})
                });
        }

        $scope.goSignup = function(){
            $location.path("/signup");
        }
    }])

    .controller('SignupCtrl', ['$scope','$auth','$location','Notification', function($scope, $auth, $location, Notification) {

        $scope.email = null;
        $scope.password = null;
        $scope.pin = null;
        $scope.signup = function(){
            $auth.signup({
                    email: $scope.email,
                    password: $scope.password,
                    pin: $scope.pin
                })
                .then(function(){
                    // Si se ha logueado correctamente, lo tratamos aquí.
                    // Podemos también redirigirle a una ruta
                    $location.path("/tweets");
                })
                .catch(function(response){
                    // Si ha habido errores llegamos a esta parte
                    Notification.error({message: response.data.message, delay: 1000, positionY: 'bottom', positionX: 'right'})
                });
        }
    }])

    .controller('IndexCtrl', ['$rootScope','$location', function($rootScope, $location) {

        $rootScope.changeView = function(view) {
            $location.path(view);
        }

    }])

    .config(['$locationProvider', '$routeProvider', '$httpProvider','$authProvider','baseDataUrl', function ($locationProvider, $routeProvider, $httpProvider, $authProvider, baseDataUrl) {
        $locationProvider.hashPrefix('!');
        $httpProvider.defaults.useXDomain = true;
        $httpProvider.defaults.withCredentials = false;
        delete $httpProvider.defaults.headers.common["X-Requested-With"];
        $httpProvider.defaults.headers.common["Accept"] = "application/json";
        $httpProvider.defaults.headers.common["Content-Type"] = "application/json";

        $authProvider.loginUrl = baseDataUrl + 'login';
        $authProvider.tokenName = 'token';
        $authProvider.tokenPrefix = 'satellizerKrypton';
        $authProvider.signupUrl = baseDataUrl + 'signup';


        $routeProvider.when('/tweets', {
            templateUrl: 'partials/tweets.html',
            controller: 'AppCtrl'
        });

        $routeProvider.when('/login', {
            templateUrl: 'partials/login.html',
            controller: 'LoginCtrl'
        });

        $routeProvider.when('/signup', {
            templateUrl: 'partials/signup.html',
            controller: 'SignupCtrl'
        });



        $routeProvider.otherwise({redirectTo: '/login'});

        $locationProvider.html5Mode(false);


    }]);



