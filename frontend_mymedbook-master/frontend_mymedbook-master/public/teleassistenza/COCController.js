myMedBookController.controller('COCController', function ($scope, $http, $stateParams, $cookies, $rootScope, OAuth, $q, $timeout, $mdDialog) {
    $scope.modelsCOC = [];
    $http.get(BASE_URL + 'COC/structure/list/').then(function (response) {
        $scope.tabs_structure = response.data;
        angular.forEach($scope.tabs_structure, function (tab_structure) {
            $scope.modelsCOC[tab_structure.pk] = []
            angular.forEach(tab_structure.actions, function (action) {
                $scope.modelsCOC[tab_structure.pk][action.action_type] = action;
            });
        });
    });
});