myMedBookController.controller('adminController', function ($scope, $http, $stateParams, $cookies, $rootScope, OAuth, $q, $timeout,$mdDialog) {
    var utente_admin= $cookies.getObject("admin")
    if(!$scope.profile || !$scope.profile.is_staff)
    {
        $http.get(BASE_URL + "profile/").then(function successCallback(response) {
            $scope.profile = response.data;
            if ($scope.profile.avatar)
                $scope.profile.avatar = URL_IMAGE + $scope.profile.avatar;
            else
                $scope.profile.avatar = IMG_DEFAULT;
            if(!$scope.profile.is_staff){
                window.location.href="#/";
                alert("Permesso negato");
            }
        })
    }
    $scope.limit = PAGE_LIMIT;
    $scope.currentPage = 1;
    $scope.offset = $scope.currentPage * $scope.limit;
    $scope.users = []
    $scope.initList = function(page){
        $http.get(BASE_URL+'users/MMBList/?page='+page).then(function(response){
            $scope.users = response.data.results;
            $scope.total_page = Math.ceil(response.data.count / $scope.limit)
            if ($scope.total_page <= 0)
                $scope.total_page = 1;
                $scope.currentPage=page;
        });
        $('.container_table_users').show()
    }

    $scope.initAdmin =function(){
        $(".user").show();
        $(".menu_init").hide();
        $(".container .menu-laterale").hide();
        $(".container .menu .menu_utenti").css("display","block !important");
        $(".container .menu .menu_utenti").show();
        $(".fa-envelope").hide();
        $(".fa-bell").hide();
        $(".fa-question-circle").hide();
        $(".fa-signout").show();
        $(".fa-signout").css("display","block !important");
        $(".benvenuto").hide();
        $(".benvenutoAdmin").css("display","block !important");
        $(".benvenutoAdmin").show();
        $scope.initList(1)
    }

    $scope.profilo_schema = schemaProfile;
    //$scope.reloadProfilo();
    $scope.data = {
        selectedIndex: 0,
        secondLocked: true,
        secondLabel: "2",
        bottom: false
    };
    $scope.openModal = function (id) {
        $scope.callRows('GET', "users", "/?id=" + id, {}, function (response_utente) {
            $scope.utente = response_utente.data;
            $("#modal_detail").modal("show");
        });
    }
    $scope.closeModal = function () {
        $("#modal_detail").modal("hide");
    }
    $scope.showDialogDetailUser = function (ev, schema, obj) {
        if (!obj)
            obj = {};
        $scope.schema = schema[0];
        $scope.obj_schema = schema;
        $scope.object = angular.copy(obj);
        $mdDialog.show({
            controller: function () {
                $scope.cancel = function () {
                    $mdDialog.cancel();
                    document.getElementById('inputDialog').click();
                };
            },
            templateUrl: 'templates/adminProfile_detail.html',
            parent: angular.element(document.body),
            targetEvent: ev,
            scope: $scope,
            preserveScope: true,
            clickOutsideToClose: true,
            fullscreen: $scope.customFullscreen // Only for -xs, -sm breakpoints.
        }).then(function (answer) {
        });
    }

    $scope.loadNext = function () {
        if ($scope.currentPage < $scope.total_page) {
            $scope.currentPage = $scope.currentPage + 1;
            $scope.initList($scope.currentPage);
        }
    };

    $scope.loadPrevious = function () {
        if ($scope.currentPage > 1) {
            $scope.currentPage = $scope.currentPage - 1;
            $scope.initList($scope.currentPage);
        }
    };

    $scope.gotoPage = function (p) {
        $scope.currentPage = p;
        $scope.initList($scope.currentPage);
    }

    $scope.range = function (min, max, step) {
        step = step || 1;
        var input = [];
        for (var i = min; i <= max; i += step) {
            input.push(i);
        }
        return input;
    };


    $scope.openDetailUser = function (user_id, ev) {
        $scope.user = user_id;
        $scope.schemaProfile = schemaProfile;
        $scope.checkEditDisabled = true;
        $scope.mymedtag = null;
        var request = [
            $http.get(BASE_URL + 'user/?structure_id=1&user_id=' + user_id).then(
                function success_response(response) {
                    $scope.profile = response.data.results[0];
                    $scope.tag_ospite = "";
                    angular.forEach($scope.profile.structureaffiliation_set, function (affiliation) {
                        angular.forEach(affiliation.mymedtag_set, function (tag) {
                            if (tag.active == true)
                                $scope.tag_ospite = tag.code;
                        });
                    })
                },
                function error_response(error_response) {
                    alert(error_response.data.detail)
                }),
            $http.get(BASE_URL + 'attribute/schema/?user_id=' + user_id).then(function success_response(response) {
                $scope.attributeSchema = response.data;
            },
                function error_response(error_response) {
                    alert(error_response.data.detail)
                }),
            $http.get(BASE_URL + 'attribute/values/?user_id=' + user_id).then(function success_response(response) {
                $scope.attributeValues = response.data;
            },
                function error_response(error_response) {
                    alert(error_response.data.detail)
                }),
        ]
        $q.all(request).then(function () {
            $http.get(BASE_URL + 'mymedtag/?code=' + $scope.tag_ospite).then(function success_response(response) {
                $scope.mymedtag = response.data;
                if ($scope.mymedtag.user.avatar)
                    $scope.mymedtag.user.avatar = URL_IMAGE + $scope.mymedtag.user.avatar;
                else
                    $scope.mymedtag.user.avatar = IMG_DEFAULT
                $scope.lista = [];
                _($scope.mymedtag.attributes_groups).forEach(function (value) {
                    if (value.attribute.datatype !== 'enum')
                        return;

                    if (($scope.lista.length > 0) && $scope.lista[value.attribute.pk])
                        $scope.lista[value.attribute.pk].value = $scope.lista[value.attribute.pk].value + ', ' + value.value;
                    else
                        $scope.lista[value.attribute.pk] = { 'name': value.attribute.name, 'value': value.value };
                });
            })
            $mdDialog.show({
                controller: function () {
                    $scope.hide = function () {
                        $mdDialog.hide();
                    };
                    $scope.cancel = function () {
                        $mdDialog.cancel();
                        document.getElementById('inputDialog').click();
                    };
                    if ($scope.profile.avatar)
                        $scope.profile.avatar = URL_IMAGE + $scope.profile.avatar;
                    else
                        $scope.profile.avatar = IMG_DEFAULT;

                    //DIALOG SALVAVITA: visualizzazione delle informazioni del salvavita
                    $scope.showDialogSalvavita = function (ev) {
                        if ($scope.user.avatar)
                            $scope.user.avatar = URL_IMAGE + $scope.user.avatar;
                        else
                            $scope.user.avatar = IMG_DEFAULT;
                        $mdDialog.show({
                            controller: function () {
                                $scope.hide = function () {
                                    $mdDialog.hide();
                                };
                                $scope.cancel = function () {
                                    $mdDialog.cancel();
                                    document.getElementById('inputDialog').click();
                                };
                            },
                            templateUrl: 'templates/showDialogSalvavita.html',
                            parent: angular.element(document.body),
                            targetEvent: ev,
                            scope: $scope,
                            preserveScope: true,
                            clickOutsideToClose: true,
                            fullscreen: $scope.customFullscreen // Only for -xs, -sm breakpoints.
                        });
                    }
                },
                templateUrl: 'templates/overlay_detail_profile.html',
                parent: angular.element(document.body),
                targetEvent: ev,
                scope: $scope,
                preserveScope: true,
                clickOutsideToClose: true,
                fullscreen: $scope.customFullscreen // Only for -xs, -sm breakpoints.
            }).then(function () {
                $scope.user = "";
                $scope.schemaProfile = {};
                $scope.initList($scope.currentPage);
            });
        });
    }

    $scope.searchUser = function(){
        if ($scope.text_user.length == 0) {
            $scope.initList(1);
            return;
        }
        if ($scope.text_user.length > 0 && $scope.text_user.length < 3)
            return;
        var path = '&path=' + $scope.text_user
        $http.get(BASE_URL + 'user/?page=1' + path).then(
            function success_response(response) {
                $scope.users = response.data.results;
                $scope.total_page = Math.ceil(response.data.count / $scope.limit)
                if ($scope.total_page <= 0)
                    $scope.total_page = 1;
                $scope.tab = 'listautenti';
                $scope.currentPage = page
            },
            function error_response(error_response) {
                alert(error_response.data.detail)
            });
    }
});

