myMedBookController.controller('profiloController', function ($scope, $http, $stateParams, $window, $q, $mdDialog, $location) {
    $("#header .user").show();
    $(".mobile").show();
    $('.mobile_MMB').show()
    $('.mobile_CDV').hide()
    window.location.href = "#/profilo";
    $scope.init = function () {
        $(".mmb_menu").removeClass('mmb_selected');
        $(".mmb_profilo").addClass('mmb_selected');
        window.location.reload;
        $scope.attributeSchema = [];
        $scope.attributeValues = [];
        $scope.schemaProfile = schemaProfile;
        $scope.checkEditDisabled = true;
        var requests = [
            $http.get(BASE_URL + "profile/").then(function successCallback(response) {
                $scope.profile = response.data;
                if ($scope.profile.avatar)
                    $scope.profile.avatar = URL_IMAGE + $scope.profile.avatar;
                else
                    $scope.profile.avatar = IMG_DEFAULT;
            }),
            /*$http.get(BASE_URL + 'attribute/schema/').then(function success_response(response) {
                $scope.attributeSchema = response.data;
            },
                function error_response(error_response) {
                    if (error_response.status === 401) {
                        window.location.href = "#/";
                        return;
                    }
                    alert(error_response.data.detail)
                }),*/
            $http.get(BASE_URL + 'attribute/values/').then(function success_response(response) {
                $scope.attributeValues = response.data;
            },
                function error_response(error_response) {
                    if (error_response.status === 401) {
                        window.location.href = "#/";
                        return;
                    }
                    alert(error_response.data.detail)
                }),
            $http.get(BASE_URL + 'mymedtag/').then(function success_response(response) {
                $scope.mymedtag = response.data;
                if ($scope.mymedtag.user.avatar)
                    $scope.mymedtag.user.avatar = URL_IMAGE + $scope.mymedtag.user.avatar;
                else
                    $scope.mymedtag.user.avatar = IMG_DEFAULT;
                $scope.setupEnums();
                /*$scope.attributeValues.forEach(function (item) {
                    item.attributes.forEach(function (attribute) {
                        if ($scope.mymedtag.lifesaver.attribute.pk == attribute.attribute.pk) {
                            if ($scope.mymedtag.lifesaver.value == 'True')
                                $scope.mymedtag.lifesaver.value = true;
                            if ($scope.mymedtag.lifesaver.value == 'False')
                                $scope.mymedtag.lifesaver.value = false;
                        }
                    });
                });*/
            },
                function error_response(error_response) {
                    if (error_response.status === 401) {
                        window.location.href = "#/";
                        return;
                    }
                    alert(error_response.data.detail);
                })];

        $q.all(requests).then(function () {
            $scope.checkEditDisabled = false;
            $scope.initCOC()
        });
    };

    $scope.data = {
        selectedIndex: 0,
        secondLocked: true,
        secondLabel: "2",
        bottom: false
    };

    $scope.next = function () {
        $scope.data.selectedIndex = Math.min($scope.data.selectedIndex + 1, 2);
    };

    $scope.previous = function () {
        $scope.data.selectedIndex = Math.max($scope.data.selectedIndex - 1, 0);
    };

    //DIALOG SALVAVITA: visualizzazione delle informazioni del salvavita
    $scope.showDialogSalvavita = function (ev) {
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

    $scope.setupEnums = function () {
        $scope.lista = [];
        _($scope.mymedtag.attributes_groups).forEach(function (value) {
            if (value.attribute.datatype !== 'enum')
                return;

            if (($scope.lista.length > 0) && $scope.lista[value.attribute.pk])
                $scope.lista[value.attribute.pk].value = $scope.lista[value.attribute.pk].value + ', ' + value.value;
            else
                $scope.lista[value.attribute.pk] = { 'name': value.attribute.name, 'value': value.value };
        });
    }

    $scope.edit = function (ev) {
        $scope.path = $location.$$path;
        $http.get(BASE_URL + "profile/").then(function successCallback(response) {
            $scope.profile = response.data;
            if ($scope.profile.avatar)
                $scope.profile.avatar = URL_IMAGE + $scope.profile.avatar;
            else
                $scope.profile.avatar = IMG_DEFAULT;
            $scope.showEditProfile(ev, $scope.profile, $scope.attributeValues, function () {
                $scope.init();
            });
        })
    }
});