myMedBookController.controller('serialsCOCController', function ($scope, $http, $stateParams, $cookies, $rootScope, OAuth, $q, $timeout, $mdDialog) {
    $scope.products = [];
    $('.mobile_MMB').show()
    $('.mobile_CDV').hide()
    $scope.codeList = function () {
        $scope.tags = [];
        $http.get(BASE_URL + 'tags/').then(function success_response(response) {
            $scope.tags = response.data;
        },
            function error_response(error_response) {
                alert(error_response.data.detail)
            });
    }
    $scope.tagList = function () {
        $http.get(BASE_URL + 'tags/').then(function success_response(response) {
            $scope.tags = response.data;
        },
            function error_response(error_response) {
                alert(error_response.data.detail)
            });
    }
    $scope.init = function () {
        $(".mmb_menu").removeClass('mmb_selected');
        $(".mmb_serials").addClass('mmb_selected');
        $http.get(BASE_URL + 'products/').then(function success_response(response) {
            $scope.products = response.data;
        },
            function error_response(error_response) {
                if (error_response.status === 401) {
                    window.location.href = "#/";
                    return;
                }
                alert(error_response.data.detail)
            });
        $scope.tags = [];
        $scope.codeList();

    }
    $scope.openModalAdd = function (tag) {
        if (tag)
            $scope.tag = tag;
        else
            $scope.tag = {};
        $('#modal_change_or_add_tag').modal('show');
    }
    $scope.createTag = function () {
        $http.post(BASE_URL + 'tags/', $scope.tag).then(function success_response(response) {
            $('#modal_change_or_add_tag').modal('hide');
            $scope.tagList();
        },
            function error_response(error_response) {
                if (error_response.status === 401) {
                    window.location.href = "#/";
                    return;
                }
                alert(error_response.data.detail)
            });
    }

    //DISATTIVA L'UTENTE COME MEMBRO DELLA STRUTTURA
    $scope.showConfirmDeactive = function (tag, ev) {
        // Appending dialog to document.body to cover sidenav in docs app
        var confirm = $mdDialog.confirm()
            .title("Conferma")
            .textContent("Sei sicuro di voler eliminare questo mymedtag?")
            .targetEvent(ev)
            .ok("Si")
            .cancel("No");

        $mdDialog.show(confirm).then(function () {
            $http.delete(BASE_URL + 'tags/' + tag.pk + '/').then(function success_response(response) {
                $('#modal_change_or_add_tag').modal('hide');
                $scope.tagList();
            },
                function error_response(error_response) {
                    alert(error_response.data.detail)
                });
        }, function () {
            // No chiudere dialog e non fare nulla
        });
    };

});