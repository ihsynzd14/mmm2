myMedBookController.controller('gestioneOspitiController', function ($scope, $http, $window, $stateParams, $rootScope, $mdDialog, $q, $location, $cookies, Upload) {

    $('.mobile_MMB').hide()
    $('.mobile_CDV').show()

    $scope.schemaProfile = schemaProfile;

    $scope.structure_id = $cookies.get('structure_id');
    $scope.user_id = null;
    $scope.limit = PAGE_LIMIT;
    $scope.currentPage = 1;
    $scope.offset = $scope.currentPage * $scope.limit;

    $scope.openUserList = function (page) {
        $scope.email = "";
        $scope.modelProfile = {};
        $http.get(BASE_URL + 'alluser/?structure_id=' + $scope.structure_id + '&affiliations=true').then(function success_response(response) {
            $scope.users_all = response.data;
        });
        $http.get(BASE_URL + 'user/?structure_id=' + $scope.structure_id + '&affiliations=true&page=' + page).then(
            function success_response(response) {
                $scope.users = response.data.results;
                $scope.total_page = Math.ceil(response.data.count / $scope.limit)
                if ($scope.total_page <= 0)
                    $scope.total_page = 1;
                $scope.tab = 'listautenti';
                $scope.currentPage = page
            },
            function error_response(error_response) {
                alert(error_response.data.detail)
            });
    }
    $scope.searchGuest = function () {
        if ($scope.text_guest.length == 0) {
            $scope.openUserList(1);
            return;
        }
        if ($scope.text_guest.length > 0 && $scope.text_guest.length < 3)
            return;
        var path = '&path=' + $scope.text_guest
        $http.get(BASE_URL + 'user/?structure_id=' + $scope.structure_id + '&affiliations=true&page=1' + path).then(
            function success_response(response) {
                $scope.users = response.data.results;
                $scope.total_page = Math.ceil(response.data.count / $scope.limit)
                if ($scope.total_page <= 0)
                    $scope.total_page = 1;
                $scope.tab = 'listautenti';
                $scope.currentPage = page
            },
            function error_response(error_response) {
                alert(error_response.data.detail)
            });
    }

    $scope.init = function () {
        $('.user').hide();
        $(".mmb_menu").removeClass('mmb_selected');
        $(".mmb_ospiti").addClass('mmb_selected');
        $scope.tab = 'listautenti';
        $scope.openUserList($scope.currentPage);
    }

    $scope.verifyGuest = function () {
        $http.get(BASE_URL + 'user/?email=' + $scope.email).then(
            function success_response(response) {
                user_id = response.data.results[0].pk;
                $scope.showIfAffiliation(user_id)
            },
            function error_response(response) {
                $scope.showConfirmAdd();
            });
    };
    $scope.verifyGuestFamiliare = function (ev) {
        $http.get(BASE_URL + 'user/?email=' + $scope.email).then(
            function success_response(response) {
                user_id = response.data.results[0].pk;
                var confirm = $mdDialog.confirm()
                    .title("Verifica la profilazione")
                    .textContent("L'utente è già profilato, si vuole aggiungere come familiare dell'ospite?")
                    .targetEvent(ev)
                    .ok("Si")
                    .cancel("No");
                $mdDialog.show(confirm).then(function () {
                    //aggiungere utente come familiare dellìospite
                    $http.get(BASE_URL + 'users/family/affiliation/?guest=' + $scope.guest_id + '&parent=' + user_id + "&structure_id=" + $scope.structure_id).then(
                        function success_response(response) {
                            alert("Relazione familiare ospite aggiunta con successo");
                            $scope.tab = 'listautenti';
                        },
                        function error_response(response) {
                            alert("Errore di sistema");
                        });
                });
            },
            function error_response(response) {
                $scope.showConfirmParent();
            });
    }

    $scope.showConfirmAdd = function (ev) {
        var confirm = $mdDialog.confirm()
            .title("Conferma")
            .textContent("Utente non trovato. Si desidera effettuare una registrazione?")
            .targetEvent(ev)
            .ok("Si")
            .cancel("No");

        $mdDialog.show(confirm).then(function () {
            //si mandare alla registrazione
            if ($scope.user_id)
                $scope.tab = 'registrationParent';
            else
                $scope.tab = 'registration';
            $scope.attributeValues = $scope.attributeSchema;
            $scope.modelProfile.email = $scope.email;
        }, function () {
            // No chiudere dialog e non fare nulla
        });
    };
    $scope.showConfirmParent = function (ev) {
        var confirm = $mdDialog.confirm()
            .title("Conferma")
            .textContent("Utente non trovato. Si desidera effettuare una registrazione?")
            .targetEvent(ev)
            .ok("Si")
            .cancel("No");

        $mdDialog.show(confirm).then(function () {
            //si mandare alla registrazione
            $scope.tab = 'registrationParent';
            $scope.modelProfile = {
                email: $scope.email
            }
        }, function () {
            // No chiudere dialog e non fare nulla
        });
    };

    $scope.showConfirmOut = function (user, ev) {
        // Appending dialog to document.body to cover sidenav in docs app
        var confirm = $mdDialog.confirm()
            .title("Conferma")
            .textContent("Sei sicuro di voler far uscire quest'ospite?")
            .targetEvent(ev)
            .ok("Si")
            .cancel("No");

        $mdDialog.show(confirm).then(function () {
            find_structureAffiliation(user, $scope.code);
            $http.delete(BASE_URL + 'structureaffiliation/' + $scope.structureaffiliation + '/').then(function success_response(response) {
                $scope.openUserList($scope.currentPage);
            })
        }, function error_response() {
            // No chiudere dialog e non fare nulla
        });
    };

    $scope.showIfAffiliation = function (user_id, ev) {

        var message = "";
        var confirm = null;
        $http.get(BASE_URL + "structureaffiliation/?user_id=" + user_id + "&structure_id=" + $scope.structure_id).then(
            function success_response(response) {
                if (response.data.length > 0) {
                    confirm = $mdDialog.confirm()
                        .title("Verifica affiliazione in struttura")
                        .textContent("L'utente fà gia parte della struttura")
                        .targetEvent(ev)
                        .ok('Ok')
                } else {
                    confirm = $mdDialog.confirm()
                        .title("Verifica affiliazione in struttura")
                        .textContent("L'utente non fa parte della struttura, si vuole creare un affiliazione?")
                        .targetEvent(ev)
                        .ok('Si')
                        .cancel('No');
                }
            },
            function error_response(response) {
                confirm = $mdDialog.confirm()
                    .title("Verifica affiliazione in struttura")
                    .textContent("L'utente non fa parte della struttura, si vuole creare un affiliazione?")
                    .targetEvent(ev)
                    .ok('Si')
                    .cancel('No');
            }).then(function () {
                $mdDialog.show(confirm).then(function () {
                    $http.post(BASE_URL + "structureaffiliation/", { guest_id: user_id, structure_id: parseInt($scope.structure_id) }).then(function (response) {
                        $scope.openUserList($scope.currentPage);
                    })
                }, function () {
                    // No chiudere dialog e non fare nulla
                });
            });
    };

    $scope.addTherapy = function (user_id, ev) {
        $scope.user_id = user_id;
        $("#modal_upload").modal("show");
    };

    $scope.$watch('files', function (files) {
        $scope.formUpload = false;
        if (files != null) {
            if (!angular.isArray(files)) {
                $timeout(function () {
                    $scope.files = files = [files];
                });
                return;
            }
            for (var i = 0; i < files.length; i++) {
                Upload.imageDimensions(files[i]).then(function (d) {
                    $scope.d = d;
                });
                $scope.errorMsg = null;
                $http.get({
                    url: BASE_URL + 'profile/'
                });
                (function (f) {
                    $scope.upload(f, true);
                })(files[i]);
            }
        }
    });

    $scope.uploadTherapy = function (file) {

        Upload.http({
            url: BASE_URL + 'upload/therapy/?user_id=' + $scope.user_id,
            headers: {
                'Content-Type': file.type,
                'Content-Disposition': "inline; filename*=UTF-8''" + encodeURI(file.name)
            },
            data: file
        }).then(function (response) {
            $("#modal_upload").modal("hide");
            $scope.allTherapy();
            $scope.user_id = '';
            $scope.picFile = null;
        }, function (response) {
            if (response.status > 0)
                $scope.errorMsg = response.status + ': ' + response.data;
            $("#modal_upload").modal("hide");
            $scope.user_id = '';
            $scope.picFile = null;
        });
    }
    $scope.setupEnums = function () {
        $scope.lista = [];
        _($scope.mymedtag.attributes_groups).forEach(function (attribute_group) {
            _(attribute_group).forEach(function (value) {
                if (value.datatype !== 'enum')
                    return;

                if (($scope.lista.length > 0) && $scope.lista[value.id_attribute])
                    $scope.lista[value.id_attribute].value = $scope.lista[value.id_attribute].value + ', ' + value.value;
                else
                    $scope.lista[value.id_attribute] = { 'name': value.name, 'value': value.value };
            });
        });
    }
    $scope.openDetailGuest = function (user_id, ev) {
        $scope.user = user_id;
        $scope.schemaProfile = schemaProfile;
        $scope.checkEditDisabled = true;
        $scope.mymedtag = null;
        var request = [
            $http.get(BASE_URL + 'user/?structure_id=' + $scope.structure_id + '&user_id=' + user_id).then(
                function success_response(response) {
                    $scope.profile = response.data.results[0];
                    $scope.tag_ospite = "";
                    angular.forEach($scope.profile.structureaffiliation_set, function (affiliation) {
                        angular.forEach(affiliation.mymedtag_set, function (tag) {
                            if (tag.active == true)
                                $scope.tag_ospite = tag.code;
                        });
                    })
                },
                function error_response(error_response) {
                    alert(error_response.data.detail)
                }),
            $http.get(BASE_URL + 'attribute/schema/?user_id=' + user_id).then(function success_response(response) {
                $scope.attributeSchema = response.data;
            },
                function error_response(error_response) {
                    alert(error_response.data.detail)
                }),
            $http.get(BASE_URL + 'attribute/values/?user_id=' + user_id).then(function success_response(response) {
                $scope.attributeValues = response.data;
            },
                function error_response(error_response) {
                    alert(error_response.data.detail)
                }),
        ]
        $q.all(request).then(function () {
                $http.get(BASE_URL + 'mymedtag/?code=' + $scope.tag_ospite).then(function success_response(response) {
                    $scope.mymedtag = response.data;
                    if ($scope.mymedtag.user.avatar)
                        $scope.mymedtag.user.avatar = URL_IMAGE + $scope.mymedtag.user.avatar;
                    else
                        $scope.mymedtag.user.avatar = IMG_DEFAULT
                    $scope.lista = [];
                    _($scope.mymedtag.attributes_groups).forEach(function (value) {
                        if (value.attribute.datatype !== 'enum')
                            return;

                        if (($scope.lista.length > 0) && $scope.lista[value.attribute.pk])
                            $scope.lista[value.attribute.pk].value = $scope.lista[value.attribute.pk].value + ', ' + value.value;
                        else
                            $scope.lista[value.attribute.pk] = { 'name': value.attribute.name, 'value': value.value };
                    });
                })
            $mdDialog.show({
                controller: function () {
                    $scope.hide = function () {
                        $mdDialog.hide();
                    };
                    $scope.cancel = function () {
                        $mdDialog.cancel();
                        document.getElementById('inputDialog').click();
                    };
                    if ($scope.profile.avatar)
                        $scope.profile.avatar = URL_IMAGE + $scope.profile.avatar;
                    else
                        $scope.profile.avatar = IMG_DEFAULT;

                    //DIALOG SALVAVITA: visualizzazione delle informazioni del salvavita
                    $scope.showDialogSalvavita = function (ev) {
                        if ($scope.user.avatar)
                            $scope.user.avatar = URL_IMAGE + $scope.user.avatar;
                        else
                            $scope.user.avatar = IMG_DEFAULT;
                        $mdDialog.show({
                            controller: function () {
                                $scope.hide = function () {
                                    $mdDialog.hide();
                                };
                                $scope.cancel = function () {
                                    $mdDialog.cancel();
                                    document.getElementById('inputDialog').click();
                                };
                            },
                            templateUrl: 'templates/showDialogSalvavita.html',
                            parent: angular.element(document.body),
                            targetEvent: ev,
                            scope: $scope,
                            preserveScope: true,
                            clickOutsideToClose: true,
                            fullscreen: $scope.customFullscreen // Only for -xs, -sm breakpoints.
                        });
                    }
                },
                templateUrl: 'templates/overlay_detail_profile.html',
                parent: angular.element(document.body),
                targetEvent: ev,
                scope: $scope,
                preserveScope: true,
                clickOutsideToClose: true,
                fullscreen: $scope.customFullscreen // Only for -xs, -sm breakpoints.
            }).then(function () {
                $scope.user = "";
                $scope.schemaProfile = {};
                $scope.openUserList($scope.currentPage);
            });
        });
    }
    /*$scope.setupEnums = function () {
        $scope.lista = [];
        _($scope.mymedtag.attributes_groups).forEach(function (attribute_group) {
            _(attribute_group).forEach(function (value) {
                if (value.datatype !== 'enum')
                    return;

                if (($scope.lista.length > 0) && $scope.lista[value.id_attribute])
                    $scope.lista[value.id_attribute].value = $scope.lista[value.id_attribute].value + ', ' + value.value;
                else
                    $scope.lista[value.id_attribute] = { 'name': value.name, 'value': value.value };
            });
        });
    }*/
    var find_structureAffiliation = function (member) {
        angular.forEach(member.structureaffiliation_set, function (item, idx) {
            if (parseInt(item.structure.pk) == $scope.structure_id) {
                if (item.mymedtag_set.length > 0) {
                    $scope.code = item.mymedtag_set[0].code;
                    $scope.tag_id = item.mymedtag_set[0].pk;
                }
                $scope.structureaffiliation = item.pk;
            }
        });
    }
    //MODIFICA O AGGIUNGE UN NUOVO TAG ALL'UTENTE SELEZIONATO
    $scope.modalChangeMMT = function (member, code) {
        $scope.member = member;
        $scope.code = "";
        find_structureAffiliation(member);
        $('#modal_change_tag').modal('show');
    }
    $scope.editMMTC = function (structureaffiliation) {
        var data = {
            'structure_affiliation': structureaffiliation,
            'code': $scope.code,
            'structure_id': $scope.structure_id
        }
        if ($scope.tag_id)
            data['pk'] = $scope.tag_id;

        $http.post(BASE_URL + 'tags_structure/', data).then(function success_response() {
            $('#modal_change_tag').modal('hide');
            $scope.openUserList($scope.currentPage);
        },
            function error_response(error_response) {
                alert(error_response.data.detail)
            })
    }

    $scope.addParent = function (user_id, ev) {
        //alert('Registrazione familiare');
        $scope.guest_id = user_id;
        $scope.user_id = user_id;
        $scope.tab = 'addfamily';

    }
    $scope.newParent = function () {
        if ($scope.modelProfile.password != $scope.modelProfile.password_check) {
            alert("Le password non combaciano")
            return;
        }
        $scope.modelProfile['guest'] = $scope.user_id;
        delete $scope.modelProfile.password_check;

        $scope.modelProfile['structure'] = parseInt($scope.structure_id);
        $http.post(BASE_URL + 'users/family/register/', $scope.modelProfile).then(
            function success_response(response) {
                $scope.openUserList($scope.currentPage);
                $scope.user_id = null;
                $scope.tab = 'listautenti';
            },
            function error_response(error_response) {
                alert(error_response.data.detail)
            }
        )
    }

    $scope.hideModalD = function () {
        $("#modal_upload").modal("hide");
    }

    $scope.allTherapy = function (ev) {
        $scope.therapy = [];

        var requests = [
            $http.get(BASE_URL + 'therapy/?user=' + $scope.user_id).then(function success_response(response) {
                $scope.therapies = response.data;
            },
                function error_response(error_response) {
                    alert(error_response.data.detail)
                }),
        ]
        $q.all(requests).then(function () {
            $scope.hideModalD();
            $("#modal_therapy").modal("show");
        })

    }

    $scope.generatePDF = function () {
        $scope.list = []

        var dd = {
            pageOrientation: 'landscape',
            content: [
                { text: 'Lista Ospiti:', fontSize: 14, bold: true, margin: [0, 20, 0, 20] },
            ],
            styles: {
                header: {
                    fontSize: 18,
                    bold: true,
                    margin: [0, 0, 0, 10]
                },
                subheader: {
                    fontSize: 16,
                    bold: true,
                    margin: [0, 10, 0, 5]
                },
                tableGuest: {
                    margin: [0, 5, 0, 15]
                },
                tableHeader: {
                    bold: true,
                    fontSize: 13,
                    color: 'black'
                },
                row: {
                    margin: [0, 15, 0, 15]
                },
                defaultStyle: {
                    alignment: 'center'
                }
            },
        }
        var subcontent = {
            style: 'tableGuest',
            table: {
                headerRows: 1,
                widths: ['*', '*', '*'],
                body: [
                    [{ text: 'Nome Ospite', style: 'tableHeader', alignment: 'center' }, { text: 'Email', style: 'tableHeader', alignment: 'center' }, { text: 'Tag Struttura', style: 'tableHeader', alignment: 'center' }],
                ]
            },
            layout: 'lightHorizontalLines'
        }
        angular.forEach($scope.users_all, function (user, idx) {
            var code = '-';
            angular.forEach(user.structureaffiliation_set, function (item, index) {
                if (parseInt(item.structure.pk) == $scope.structure_id) {
                    if (item.mymedtag_set.length > 0) {
                        item.mymedtag_set.forEach(function (mymedtag) {
                            if (mymedtag.active == true)
                                code = mymedtag.code;
                        })
                    }
                    else {
                        code = '-';
                    }
                }
                if (index >= user.structureaffiliation_set.length - 1) {
                    if (!code)
                        code = '-'
                    subcontent.table.body.push([{ 'text': user.first_name + ' ' + user.last_name, style: 'row', alignment: 'center' }, { 'text': user.email, style: 'row', alignment: 'center' }, { 'text': code, style: 'row', alignment: 'center' }])
                }
            });
            if (idx >= $scope.users_all.length - 1) {
                dd.content.push(subcontent)
                pdfMake.createPdf(dd).print();
            }
        })
    }
    $scope.editProfile = function (ev) {
        $scope.showEditProfile(ev, $scope.profile, $scope.attributeValues);
    }
    $scope.newGuest = function () {
        $scope.tab = 'adduser';
        $scope.attributeValues = $scope.attributeSchema;
    }

    $scope.loadNext = function () {
        if ($scope.currentPage < $scope.total_page) {
            $scope.currentPage = $scope.currentPage + 1;
            $scope.openUserList($scope.currentPage);
        }
    };

    $scope.loadPrevious = function () {
        if ($scope.currentPage > 1) {
            $scope.currentPage = $scope.currentPage - 1;
            $scope.openUserList($scope.currentPage);
        }
    };

    $scope.gotoPage = function (p) {
        $scope.currentPage = p;
        $scope.openUserList($scope.currentPage);
    }

    $scope.range = function (min, max, step) {
        step = step || 1;
        var input = [];
        for (var i = min; i <= max; i += step) {
            input.push(i);
        }
        return input;
    };

    $scope.openFileTherapies = function (file_path) {
        partial_path = file_path.split('therapy/')
        if (partial_path[1])
            window.open(URL_IMAGE + partial_path[1], '_blank');
        else
            window.open(URL_IMAGE + file_path, '_blank');
    }

    $scope.deleteDocumentTherapy = function (ev, document_pk, user_id) {
        $("#modal_therapy").modal("hide");
        $scope.showConfirm(ev, 'document', document_pk, function () {
            $scope.user_id=user_id;
            $scope.allTherapy();
        })
    }
});
