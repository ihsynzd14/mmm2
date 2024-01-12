myMedBookController.controller('menuController', function ($scope, $http, $stateParams, $mdDialog) {
    $scope.IMG_DEFAULT = IMG_DEFAULT;
    $scope.gestioneStruttura=false;
/*    $scope.callRows('GET', 'profile/detail/', "", {}, function(response){
        if(response[0].avatar)
            response[0].avatar = URL_IMAGE + response[0].avatar;
        $scope.profileDetail = response;
    });
*/
    //TOOLTIP
    $scope.tooltipMenuDetail="Visualizza e modifica i dettagli del tuo profilo, le informazioni su di te e sul tuo stato di salute";
    $scope.tooltipMenuPrivacy="Visualizza e modifica le impostazioni della privacy relative alle informazioni presenti nel tuo profilo";
    $scope.tooltipMyMedTag="Visualizza e modifica i tuoi Mymedtag";
    $scope.tooltipChangePassword = "Modifica la tua password";
    $scope.tooltipPublicLifesaver = "Dopo aver selezionato le informazioni da includere nelle altre sezioni, seleziona l'informazione principale, che sarà visualizzata per prima e a cui l'azione farà riferimento.";
    $scope.image=IMG_DEFAULT;

    function getContextFromUrl(){
        var url = window.location.href;
        var vect_elem_url = url.split("/");
        return vect_elem_url[vect_elem_url.length-1];
    }

});