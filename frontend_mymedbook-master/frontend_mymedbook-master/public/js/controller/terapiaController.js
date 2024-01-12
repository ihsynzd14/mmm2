myMedBookController.controller('terapiaController', function ($scope, $http, $stateParams, $q, $timeout, $mdDialog, OAuthToken) {
    $scope.terapia_schema = terapia_schema;
    $('.mobile_MMB').show()
    $('.mobile_CDV').hide()
    $scope.split_terapie = function () {
        $scope.terapie_in_corso = [];
        $scope.terapie_archiviate = [];
        if ($scope.terapie.length <= 0) {
            $("#loader_terapia").hide();
            $("#loader_terapia_arch").hide();
            $("#empty_terapy_in_corso").show();
            $("#empty_terapy_archiviate").show();
        } else {
            angular.forEach($scope.terapie, function (terapia, idx) {
                if (!terapia.start_date && !terapia.end_date) {
                    terapia.start_date = terapia.modified
                    terapia.end_date = terapia.modified
                    terapia.drug = "Terapia"
                }
                terapia.start_date = $scope.formatDate(terapia.start_date);
                terapia.end_date = $scope.formatDate(terapia.end_date);
                var check_date = $scope.checkCurrentDate(terapia.start_date, terapia.end_date);
                if (check_date === true && terapia.active === true) {
                    $scope.terapie_in_corso.push(terapia);
                } else {
                    $scope.terapie_archiviate.push(terapia);
                }
                if (idx === $scope.terapie.length - 1) {
                    $("#loader_terapia").hide();
                    $("#loader_terapia_arch").hide();
                    if ($scope.terapie_in_corso.length <= 0)
                        $("#empty_terapy_in_corso").show();
                    else
                        $("#empty_terapy_in_corso").hide();
                    if ($scope.terapie_archiviate.length <= 0)
                        $("#empty_terapy_archiviate").show();
                    else
                        $("#empty_terapy_archiviate").hide();
                }
            });
        }
    }
    $scope.load = function () {
        $(".mmb_menu").removeClass('mmb_selected');
        $(".mmb_terapia").addClass('mmb_selected');
        var token = OAuthToken.getToken();
        $scope.callRows('GET', "therapy", "/", {}, function (response_terapie) {
            $scope.terapie = response_terapie;
            $scope.split_terapie();
        });
        $scope.callRows('GET', "dossier", '/', {}, function (response) {
            terapia_schema[0].items[10].options = response;
        });
    }
    //funzione che chiama la dialog per la creazione e/o modifica di un oggetto
    $scope.actionObjects = function ($event, terapia_schema, action, obj) {
        $scope.showEditNew($event, terapia_schema, action, obj, function () {
            $scope.load();
        });
    }

    //si puo visualizzare il bottone di modifica solo entro i due giorni dall'inserimento della terapia'
    $scope.showButtonEdit = function (createdAt) {
        if (!createdAt)
            return true;
        return $scope.checkDifferentBetweenDate(createdAt, NUM_GG_EDIT_THERAPY);
    }
    $scope.conferma = function (ev, id) {
        $scope.showConfirm(ev, "therapy", id, function () {
            $scope.load();
            $scope.assignEvent();
        });
    }
    //per disattivare la terapia modificare il campo "attivo della terapia
    //e portarlo in terapie_archiviate
    $scope.deactiveTerapy = function (id_terapy) {
        $scope.callRows("PUT", "therapy", "/" + id_terapy + "/", { "active": false }, function (response) {
            $scope.load();
        });
    }

    var flagSalvavitaAttivo = true;
    $scope.intoSalvavita = function (vect) {
        vect.lifesaver = !vect.lifesaver;
        $scope.callRows("PUT", "therapy", "/" + vect.pk + "/", { "lifesaver": vect.lifesaver }, function (response) {
            $scope.load();
        });

    }

    $scope.deleteDocumentTherapy = function (ev, document_pk) {
        $scope.showConfirm(ev, 'document', document_pk, function () {
            $scope.load();
        })
    }

});