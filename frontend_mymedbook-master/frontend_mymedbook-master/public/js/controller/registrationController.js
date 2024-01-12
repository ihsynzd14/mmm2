myMedBookController.controller('registrationController', function ($scope, $http) {
    $scope.model = {};

    $scope.init = function () {
        $scope.attributeSchema = [];
        $scope.attributeValues = [];
        $scope.checkRegDisabled = true;
        $scope.schemaProfile = schemaRegistration;
        $http.get(BASE_URL + 'attribute/values/').then(function success_response(response) {
            $scope.attributeValues = response.data;
            $scope.checkRegDisabled = false;
        },
            function error_response(error_response) {
                if (error_response.status === 401) {
                    window.location.href="#/";
                }
                alert(error_response.data.detail)
            });
    };

    $scope.save = function () {
        if(!$scope.modelProfile.first_name || !$scope.modelProfile.last_name || !$scope.modelProfile.email){
            alert('Compilare tutti i campi obbligatori')
            return;
        }
        $scope.modelProfile.password = 'ospiteospite'

        $scope.modelProfile.birthday = $scope.formatDateinDB($scope.modelProfile.birthday)
        var attributes = [];
        angular.forEach($scope.attributeValues, function (tab) { attributes = attributes.concat(tab.attributes); });

        $scope.modelProfile.structure_id = $scope.structure_id;
        $http.post(BASE_URL + "register/", $scope.modelProfile, { 'Content-Type': "application/json" }).then(function success_response(response) {
            $scope.callRows("PUT", "profile/editattributes", "/?guest_id=" + response.data.pk, { data: attributes }).then(function () {
                window.location.reload();
            });
        },
            function error_response(error_response) {
                if (error_response.status === 401) {
                    window.location.href="#/";
                    return;
                }
                alert(error_response.data.detail)
            });
    }
});
