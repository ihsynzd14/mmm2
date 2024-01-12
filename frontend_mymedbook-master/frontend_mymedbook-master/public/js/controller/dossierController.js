myMedBookController.controller('dossierController', function ($scope, $http, $stateParams, $mdDialog, $timeout, OAuthToken) {
      $scope.dossier_schema = dossier_schema;
      $scope.tooltip1 = "Crea un dossier medico per te e per i tuoi familiari, caricando foto e/o file.\nMantieni in un unico posto i referti medici e le prescrizioni."
      $scope.dossiers = []
      $scope.input_blocked = false;
      $('.mobile_MMB').show()
      $('.mobile_CDV').hide()
      $scope.load = function () {
            $(".mmb_menu").removeClass('mmb_selected');
            $(".mmb_dossier").addClass('mmb_selected');
            //var token = OAuthToken.getToken();
            $("#loader_dossier").hide();
            $scope.callRows("GET", "dossier/", '', {}, function (data) {
                  if (data.length <= 0)
                        $("#loader_dossier").hide();
                  $scope.dossiers = data;
                  $http.post(BASE_URL + 'devices/checkNotificationAsRead/', { 'item_idx': [], 'item_type': 'dossier' }).then(
                        function () {
                              $http.get(BASE_URL + 'devices/notifications/').then(function (response) {
                                    $scope.notifications = response.data;
                              });
                        }
                  )
            });
      }
      $scope.conferma = function (ev, id) {
            $scope.showConfirm(ev, 'dossier', id, function () {
                  $scope.load();
            });
      }
      $scope.createNew = function ($event) {
            $scope.callRows('GET', "circle", '/', {}, function (response) {
                  dossier_schema[0].items[3].options = response;
                  $scope.showEditNew($event, dossier_schema, "Crea", null, function (response) {
                        $scope.load();
                  });
            });

      }
      $scope.openDetail = function ($event, obj) {
            //var index = $scope.indexElementInVector(idx, $scope.dossiers);
            $scope.callRows('GET', "circle", '/', {}, function (response) {
                  dossier_schema_detail[0].items[3].options = response;
                  $scope.callRows('GET', "dossier", '/'+obj.pk+'/', {}, function (response) {
                        $scope.showDialogDetail($event, dossier_schema_detail, response, function () {
                              $scope.load();
                        });
                  });
            });


      }
      $scope.newFile = function ($ev, familiare_id) {
            $scope.showEditNew($ev, files_schema, "Aggiungi", null, function (response) {
                  $scope.load();
            }, familiare_id)
      }
});

