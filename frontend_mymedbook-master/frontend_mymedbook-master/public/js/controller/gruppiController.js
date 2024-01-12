myMedBookController.controller('gruppiController', function ($scope, $http, $stateParams, $timeout, $compile, OAuthToken) {

    $(".mmb_menu").removeClass('mmb_selected');
    $(".mmb_gruppi").addClass('mmb_selected');
    $('.mobile_MMB').show()
    $('.mobile_CDV').hide()
    $scope.init = function () {
        $http.get(BASE_URL + "circle/").then(function (response) {
            $scope.gruppi = response.data;
            $scope.item_idx = [];
            angular.forEach(response.data, function (item) {
                console.log(item.pk)
                $scope.item_idx.push(item.pk)
            });
            $http.post(BASE_URL + 'devices/checkNotificationAsRead/', { 'item_idx': [], 'item_type': 'circle' }).then(
                function () {
                    $http.get(BASE_URL + 'devices/notifications/').then(function (response) {
                        $scope.notifications = response.data;
                    });
                }
            )
        });
    }
    $scope.newGroup = function (ev) {
        $scope.showEditNew(ev, gruppo_schema, "Crea", null, function () {
            $scope.init();
        });
    }
    $scope.edit = function (ev, obj) {
        $http.get(BASE_URL + 'circle/' + obj.pk + '/').then(function (response) {
            circle = response.data
            if (circle.circleaffiliation_set.length > 0) {
                angular.forEach(circle.circleaffiliation_set, function (item, index) {
                    var email = '';
                    if (item.email)
                        email = item.email
                    var tmp = { 'email': email };
                    circle.circleaffiliation_set[index] = tmp;
                });
            }

            $scope.showEditNew(ev, gruppo_schema, "Modifica", circle, function () {
                $scope.init();
            });
        });

    }
    $scope.detail = function (ev, obj) {
        $http.get(BASE_URL + 'circle/' + obj.pk + '/').then(function (response) {
            $scope.showDialogDetail(ev, gruppo_schema, response.data, function () {
                $scope.init();
            });
        });
    }
    $scope.conferma = function (ev, id) {
        $scope.showConfirm(ev, "circle", id, function () {
            $scope.reloadProfilo();
            $scope.init();
        });
    }

});