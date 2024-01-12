myMedBookController.controller('ingressiController', function ($scope, $http, $stateParams, $mdDialog, $rootScope, $q, $location, $cookies) {
    $scope.structure_id = '';
    $scope.header = 'initial';
    $scope.tab = 'elenco_strutture';
    $scope.lunghezza = null;
    $scope.path = '';
    var user_id = null;

    $scope.init = function () {
        $(".mmb_menu").removeClass('mmb_selected');
        $(".mmb_strutture").addClass('mmb_selected');
        $('.mobile_MMB').show()
        $('.mobile_CDV').hide()
    }
    $scope.openUserList = function (structure_id) {

        $cookies.put('structure_id', structure_id);
        if ($scope.profile.groups[0].name.indexOf('admin_coc') >= 0) {
            window.open(
                $location.$$absUrl.replace($location.$$path, 'gestioneAffiliatiCOC'),
                '_blank' // <- This is what makes it open in a new window.
            );
            $scope.path = $location.$$path;
            return;
        }
        if ($scope.profile.groups[0].name.indexOf('operatore_coc') >= 0) {
            window.open(
                $location.$$absUrl.replace($location.$$path, 'gestioneRichiesteCOC'),
                '_blank' // <- This is what makes it open in a new window.
            );
            $scope.path = $location.$$path;
            return;
        }
        /*
        if ($scope.profile.groups[0].name.indexOf('portiere') >= 0) {
            $scope.openAlarm();
            return;
        }*/

        window.open(
            $location.$$absUrl.replace($location.$$path, 'ospiti'),
            '_blank' // <- This is what makes it open in a new window.
        );

        $scope.path = $location.$$path;
    }


});
