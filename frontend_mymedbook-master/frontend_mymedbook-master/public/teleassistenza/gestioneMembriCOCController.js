myMedBookController.controller('gestioneMembriCOCController', function ($scope, $http, $window, $stateParams, $rootScope, $mdDialog, $q, $location, $cookies) {
    $('.mobile_MMB').hide()
    $('.mobile_CDV').show()
    $scope.tab = 'listautenti';
    $scope.structure_id = $cookies.get('structure_id');
    $scope.listLabelGroups = listLabelGroups;

    $scope.limit = PAGE_LIMIT;
    $scope.currentPage = 1;
    $scope.offset = $scope.currentPage * $scope.limit;
    //LISTA DI UTENTI MEMBRI DELLA STRUTTURA
    $scope.membersList = function (page) {
        $scope.email="";
        $http.get(BASE_URL + 'user/?structure_id=' + $scope.structure_id + '&members=true&page=' + page).then(
            function successCallback(response) {
                $scope.users = response.data.results;
                $scope.tab = 'listautenti';
                $scope.total_page = Math.ceil(response.data.count / $scope.limit)
                if($scope.total_page<=0)
                    $scope.total_page=1;
                $scope.tab = 'listautenti';
                $scope.currentPage = page;
            },
            function errorCallback(error_response) {
                if (error_response.status === 401) {
                    window.location.href = "#/";
                    return;
                }
                alert(error_response.data.detail)
            });
    }

    $scope.init = function () {
		$('.user').hide();
        $scope.groups = [];
        $http.get(BASE_URL + 'group/').then(function successCallback(response) {
            angular.forEach(response.data, function (group) {
                //group['text'] = listLabelGroups[group.name]['text']
                $scope.groups.push(group);
            },
                function errorCallback(error_response) {
                    if (error_response.status === 401) {
                        window.location.href = "#/";
                        return;
                    }
                    alert(error_response.data.detail)
                });
        });
        $(".mmb_menu").removeClass('mmb_selected');
        $(".mmb_dipendenti").addClass('mmb_selected');
        $scope.tab = 'listautenti';
        $scope.membersList(1);
    }

    //VERIFICA CHE L'UTENTE SIA GIA' PRESENTE NEL SISTEMA
    $scope.verifyGuest = function () {
        $http.get(BASE_URL + 'user/?email=' + $scope.email).then(
            function successCallBack(response) {
                if (response.data.results.length > 0) {
                    user_id = response.data.results[0].pk;
                    $scope.showIfMember(response.data.results[0], user_id)
                }
            },
            function errorCallback() {
                $scope.showConfirm();
            });
    };

    //SE L'UTENTE NON È GIA PRESENTE NEL DB CHIEDE DI REGISTRARLO
    $scope.showConfirm = function (ev) {
        // Appending dialog to document.body to cover sidenav in docs app
        var confirm = $mdDialog.confirm()
            .title("Conferma")
            .textContent("Utente non trovato. Si desidera effettuare una registrazione?")
            .targetEvent(ev)
            .ok("Si")
            .cancel("No");

        $mdDialog.show(confirm).then(function () {
            //si mandare alla registrazione
            $scope.header = 'registration';
            $scope.tab = 'registration';
            $scope.modelProfile.email = $scope.email;
        }, function () {
            // No chiudere dialog e non fare nulla
        });
    };

    var find_structureMembership = function (member) {
        angular.forEach(member.structuremembership_set, function (item, idx) {
            if (parseInt(item.structure.pk) == $scope.structure_id) {
                if (item.mymedtag_set.length > 0) {
                    $scope.code = item.mymedtag_set[0].code;
                    $scope.tag_id = item.mymedtag_set[0].pk;
                }
                $scope.structuremembership = item.pk;
            }
        });
    }
    //MODIFICA O AGGIUNGE UN NUOVO TAG ALL'UTENTE SELEZIONATO
    $scope.modalChangeMMT = function (member, code) {
        $scope.member = member;
        $scope.code = "";
        find_structureMembership(member);
        $('#modal_change_tag').modal('show');
    }
    $scope.editMMTC = function (structuremembership, tag_id) {
        var data = {
            'structure_membership': structuremembership,
            'code': $scope.code,
            'structure_id': $scope.structure_id
        }
        if (tag_id)
            data['pk'] = tag_id;

        $http.post(BASE_URL + 'tags_structure/', data).then(function successCallBack() {
            $('#modal_change_tag').modal('hide');
            $scope.membersList($scope.currentPage);
        },
            function errorCallback(error_response) {
                if (error_response.status === 401) {
                    window.location.href = "#/";
                    return;
                }
                alert(error_response.data.detail)
            })
    }

    //DISATTIVA L'UTENTE COME MEMBRO DELLA STRUTTURA
    $scope.showConfirmOut = function (user, ev) {
        // Appending dialog to document.body to cover sidenav in docs app
        var confirm = $mdDialog.confirm()
            .title("Conferma")
            .textContent("Sei sicuro di voler far uscire quest'ospite?")
            .targetEvent(ev)
            .ok("Si")
            .cancel("No");

        $mdDialog.show(confirm).then(function () {
            find_structureMembership(user, $scope.code);
            $http.delete(BASE_URL + 'structuremembership/' + $scope.structuremembership + '/').then(function successCallback(response) {
                $scope.tab = 'listautenti';
                $scope.membersList($scope.currentPage);
            },
                function errorCallback(error_response) {
                    if (error_response.status === 401) {
                        window.location.href = "#/";
                        return;
                    }
                    alert(error_response.data.detail)
                })
        }, function () {
            // No chiudere dialog e non fare nulla
        });
    };

    //CONTROLLA CHE L'UTENTE SELEZIONATO SIA GIÀ MEMBRO DELLA TRUTTURA
    $scope.showIfMember = function (user, user_id, ev) {

        var message = "";
        var confirm = null;
        var member_aff_pk = "";

        $http.get(BASE_URL + "structuremembership/?user_id=" + user_id + "&structure_id=" + $scope.structure_id).then(
            function success_response(response) {
                if (response.data.length > 0) {
                    if(response.data[0].left){
                        member_aff_pk = response.data[0].pk
                        message = "La mail indicata è associata a "+ user.first_name + " " + user.last_name + " cessato in data " +
                        response.data[0].left + ". Vuoi riattivarlo?"
                        confirm = $mdDialog.confirm()
                            .title("Verifica relazione in struttura")
                            .textContent(message)
                            .targetEvent(ev)
                            .ok('Si')
                            .cancel('No');
                    }
                    else{
                        confirm = $mdDialog.confirm()
                            .title("Verifica relazione in struttura")
                            .textContent("L'operatore fà gia parte della struttura")
                            .targetEvent(ev)
                            .ok('Ok')
                    }
                }
                else{
                    confirm = $mdDialog.confirm()
                        .title("Verifica relazione in struttura")
                        .textContent("L'utente non fa parte della struttura, si vuole associare come dipendente?")
                        .targetEvent(ev)
                        .ok('Si')
                        .cancel('No');
                }
            },
            function error_response(response) {
                confirm = $mdDialog.confirm()
                    .title("Verifica relazione in struttura")
                    .textContent("L'utente non fa parte della struttura, si vuole associare come dipendente?")
                    .targetEvent(ev)
                    .ok('Si')
                    .cancel('No');

            }).then(function () {
                if(member_aff_pk){
                    $mdDialog.show(confirm).then(function () {
                        $http.put(BASE_URL + "structuremembership/"+member_aff_pk+"/", { left: null }).then(function (response) {
                            $scope.membersList($scope.currentPage);
                        })
                    }, function () {
                        // No chiudere dialog e non fare nulla
                    });
                }
                else{
                    $mdDialog.show(confirm).then(function () {
                        $http.post(BASE_URL + "structuremembership/", { user_id: user_id, structure_id: parseInt($scope.structure_id) }).then(function (response) {
                            $scope.membersList($scope.currentPage);
                        })
                    }, function () {
                        // No chiudere dialog e non fare nulla
                    });
                }
            });

    };
    //SALVA UN UTENTE COME AFFILIATO MYMEDBOOK E MEMBER DELLA STRUTTURA
    $scope.saveMember = function () {
        if ($scope.modelProfile.password != $scope.modelProfile.password_check) {
            alert("Le password non coincidono")
            return;
        }
        delete $scope.modelProfile.password_check
        $scope.modelProfile['structure'] = parseInt($scope.structure_id);
        $scope.modelProfile['group'] = 7;
        $http.post(BASE_URL + 'users/members/register/', $scope.modelProfile).then(
            function successCallback(response) {
                $scope.email = "";
                $scope.modelProfile = {}
                $scope.membersList($scope.currentPage);
            },
            function errorCallback(error_response) {
                if (error_response.status === 401) {
                    window.location.href = "#/";
                    return;
                }
                alert(error_response.data.detail)
            }
        )
    }

    $scope.loadNext = function () {
        if ($scope.currentPage < $scope.total_page) {
            $scope.currentPage = $scope.currentPage + 1;
            $scope.membersList($scope.currentPage);
        }
    };

    $scope.loadPrevious = function () {
        if ($scope.currentPage > 1) {
            $scope.currentPage = $scope.currentPage - 1;
            $scope.membersList($scope.currentPage);
        }
    };

    $scope.gotoPage = function (p) {
        $scope.currentPage = p;
        $scope.membersList($scope.currentPage);
    }

    $scope.range = function (min, max, step) {
        step = step || 1;
        var input = [];
        for (var i = min; i <= max; i += step) {
            input.push(i);
        }
        return input;
    };
});
