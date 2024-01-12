myMedBookController.controller('privacyController', function ($scope, $http, $stateParams) {

    $scope.init = function () {
        $(".mmb_menu").removeClass('mmb_selected');
        $(".mmb_privacy").addClass('mmb_selected');
        $('.mobile_MMB').show()
        $('.mobile_CDV').hide()
    }
    $scope.modifiedLifesaver = function(){
        $scope.callRows("PUT", "profile/edit/", "", { data: $scope.profile });
    }

});