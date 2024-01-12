'use strict';
/*sono i moduli rispettivi di ogni libreria, nel caso di ngRoute serve ad esempio per utilizzare il $routeProvider*/
var app = angular.module('myMedBookApp', [
    'angular-oauth2',
    'ngRoute',
    'ngResource',
    'ngMaterial',
    'ui.bootstrap',
    'ngCookies',
    'mgcrea.ngStrap',
    'ngFileUpload'
]);
function isSecure() {
    return (window.location.protocol === 'https:');
}
app.config(['$routeProvider', '$sceDelegateProvider', '$httpProvider', '$mdDateLocaleProvider', 'OAuthProvider', 'OAuthTokenProvider', '$provide', '$resourceProvider','$compileProvider',
    function ($routeProvider, $sceDelegateProvider, $httpProvider, $mdDateLocaleProvider, OAuthProvider, OAuthTokenProvider, $provide, $resourceProvider, $compileProvider) {
        $routeProvider.
            when('/', {
                templateUrl: 'mymedtag.html',
                controller: 'mymedtagController'
            }).
            when('/login', {
                templateUrl: 'login.html',
                controller: 'loginController'
            }).
            otherwise({
                redirectTo: '/'
            });
        $provide.decorator('$q', function ($delegate) {
            function seqAll(promises) {
                var d = $delegate.defer();
                var results = [];
                var i = 0;

                recurse(promises[i]);

                function recurse(promise) {
                    i++;
                    promise.then(function (data) {
                        results.push(data);
                        if (i < promises.length)
                            recurse(promises[i]);
                        else
                            d.resolve(results);
                    }).catch(function (error) {
                        d.reject('promises[' + (i - 1) + ']' + ' rejected with error: ' + error);
                    });
                }
                return d.promise;
            }
            $delegate.seqAll = seqAll;
            return $delegate;
        });
        $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|chrome-extension|intent):/);
        //OAuth
        OAuthProvider.configure({
            baseUrl: URL_AUTH,
            clientId: CLIENT_ID,
            grantPath: '/oauth/token/',
            revokePath: '/oauth/revoke/'
        });
        OAuthTokenProvider.configure({
            name: 'token',
            options: {
                secure: isSecure()
            }
        });

    }
]).directive("hideToolbar", function () {
    return {
        restrict: 'AEC',
        link: function (scope, elem, attr) {
            $(".fc-toolbar").hide();
        }
    }
}).run(['$rootScope', '$window', 'OAuth', function ($rootScope, $window, OAuth) {
    $rootScope.$on('oauth:error', function (event, rejection) {
        // Ignore `invalid_grant` error - should be catched on `LoginController`.
        if ('invalid_grant' === rejection.data.error) {
            return $window.location.href = '#/';
        }

        // Refresh token when a `invalid_token` error occurs.
        if ('invalid_token' === rejection.data.error) {
            return OAuth.getRefreshToken();
        }

        // Redirect to `/login` with the `error_reason`.
        return $window.location.href = '#/';
    });

}]).controller('loginController', function ($scope, $http, $cookies, $rootScope, OAuth, $q, $timeout) {
    $cookies.remove("profilo");
    $cookies.remove("token");
    $("#header .user").hide();
    function refreshToken(OAuth) {
        OAuth.getRefreshToken().then(function (response) {
            $timeout(refreshToken, response.data.expires_in / 2 * 1000, true, OAuth);
        });
    }
    $scope.login = function () {
        if (!$scope.email || !$scope.password)
            return;
        (function () {
            if (!OAuth.isAuthenticated())
                return $q.resolve();
            return OAuth.revokeToken();
        })().then(function () {
            OAuth.getAccessToken({ username: $scope.email, password: $scope.password })
                .then(
                function successCallback(success_response) {
                    window.location.href = "#/";
                    $timeout(refreshToken, success_response.data.expires_in / 2 * 1000, true, OAuth);
                }, function errorCallback(error_response) {
                    if (error_response.status === 401) {
                        alert("Username o password non valida");
                    }
                    /*if (error_response.status === 500) {
                        alert("La lunghezza minima non puo essere meno di 4 caratteri");
                    }*/
                    if (error_response.status === 403) {
                        alert("Email o password errate");
                    }
                    else
                        alert("errore di sistema")
                });
        });
    }
}).controller('mymedtagController', function ($scope, $http, $cookies, $routeParams, $rootScope, OAuth, $q, $timeout, $location, OAuthToken) {
    var token = OAuthToken.getToken();

    $scope.getParameterByName = function (name) {
        var url = window.location.href;
        name = name.replace(/[\[\]]/g, "\\$&");
        var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"), results = regex.exec(url);
        if (!results) return null;
        if (!results[2]) return '';
        return decodeURIComponent(results[2].replace(/\+/g, " "));
    }

    $scope.code = $scope.getParameterByName('code');
    console.log($scope.code)
    /*if (window.navigator.userAgent.indexOf('Android') != -1) {
        $("#modal_MMT").modal("show");
    }*/
    if (window.navigator.userAgent.indexOf('Android') != -1) {
        console.log($scope.code)
        $(".app_view").show();
    }
    if (!$scope.code) {
        window.location.href = "#/login";
    }

    var query_string = "";
    $scope.IMG_DEFAULT = "../" + IMG_DEFAULT;
    if ($scope.code) {
        query_string = '?code=' + $scope.code;
    }
    $scope.init = function () {
        $http({
            method: 'GET',
            url: BASE_URL + 'mymedtag/' + query_string,
            data: {},
            withCredentials: false,
            headers: {
                'Content-Type': "application/json"
            }
        }).then(
            function successCallback(success_response) {
                $scope.mymedtag = success_response.data;
                if ($scope.mymedtag.user.avatar)
                    $scope.mymedtag.user.avatar = URL_IMAGE + $scope.mymedtag.user.avatar;
                else
                    $scope.mymedtag.user.avatar = $scope.IMG_DEFAULT;
                $scope.lista = [];
                $scope.mymedtag.attributes_groups.forEach(function (value) {
                    if (value.attribute.datatype !== 'enum')
                        return;

                    if (($scope.lista.length > 0) && $scope.lista[value.attribute.pk])
                        $scope.lista[value.attribute.pk].value = $scope.lista[value.attribute.pk].value + ', ' + value.value;
                    else
                        $scope.lista[value.attribute.pk] = { 'name': value.attribute.name, 'value': value.value };
                });
            },
            function errorCallback(error_callback){
                window.location.href = "#/";
            });
    }
    $scope.isEmpty = function (obj) {
        for (var i in obj) if (obj.hasOwnProperty(i)) return false;
        return true;
    };
    $scope.openFile = function (file_path) {
        window.open(URL_IMAGE + file_path, '_blank');
    }
    /*$scope.index_class=0;
    $scope.changeClass = function(){
        $scope.index_class=$scope.index_class+1;
        if($scope.index_class%3==0)
            return "boxmmt3"
        else if ($scope.index_class%3==1)
            return "boxmmt2"
        else
            return "boxmmt1"
    }*/
});