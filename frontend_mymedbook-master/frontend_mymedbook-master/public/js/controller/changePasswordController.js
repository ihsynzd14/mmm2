myMedBookController.controller('changePasswordController', function ($scope, $http, $stateParams, $window) {
    $(".mmb_menu").removeClass('mmb_selected');
    $(".mmb_change_password").addClass('mmb_selected');
    $scope.changePassword = function () {
        if ($scope.new_password!==$scope.password_repeated) {
            alert("Le password non corrispondono")
            return;
        }
        $http.post(BASE_URL+'change_password/', {'old_password':$scope.old_password, 'new_password':$scope.new_password}).then(
            function success_response(response){
                alert("Password cambiata con successo");
                $window.location.href = "#/profilo";
            },
            function error_response(error){
                if(error.data.detail)
                    alert(error.data.detail)
                else
                    alert("Password attuale non corretta")
            });
    }
});