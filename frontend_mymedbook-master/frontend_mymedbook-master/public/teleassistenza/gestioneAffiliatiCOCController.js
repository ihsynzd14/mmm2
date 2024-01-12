myMedBookController.controller('gestioneAffiliatiCOCController', function ($scope, $http, $window, $stateParams, $rootScope, $mdDialog, $q, $location, $cookies, Upload) {
    console.log("affiliati")
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
        $http.get(BASE_URL + 'products/').then(function success_response(response) {
            $scope.products = response.data;
        },
            function error_response(error_response) {
                if (error_response.status === 401) {
                    window.location.href = "#/";
                    return;
                }
                alert(error_response.data.detail)
            });
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
                $scope.showConfirm();
            });
    };

    $scope.showConfirm = function (ev) {
        var confirm = $mdDialog.confirm()
            .title("Conferma")
            .textContent("Utente non trovato. Si desidera effettuare una registrazione?")
            .targetEvent(ev)
            .ok("Si")
            .cancel("No");

        $mdDialog.show(confirm).then(function () {
            $scope.tab = 'registration';
            $scope.attributeValues = $scope.attributeSchema;
            $scope.modelProfile.email = $scope.email;
        }, function () {
            // No chiudere dialog e non fare nulla
        });
    };

    $scope.showConfirmOut = function (user, ev) {
        // Appending dialog to document.body to cover sidenav in docs app
        var confirm = $mdDialog.confirm()
            .title("Conferma")
            .textContent("Sei sicuro di voler far uscire quest'utente?")
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
    $scope.modalMMT = function (user) {
        $scope.userMMTag = user;
        $http.get(BASE_URL + 'COC/MMTCode/?user_id=' + user.pk + '&structure_id=' + $scope.structure_id).then(function (response) {
            $scope.usercodes = response.data;
            $('#modal_change_tag').modal('hide');
            $("#modal_MMTCOC").modal("show")
        });
    }
    //MODIFICA O AGGIUNGE UN NUOVO TAG ALL'UTENTE SELEZIONATO
    $scope.modalChangeMMT = function () {
        $scope.code_new = "";
        find_structureAffiliation($scope.userMMTag);
        $("#modal_MMTCOC").modal("hide")
        $('#modal_change_tag').modal('show');
    }
    $scope.editMMTC = function (structureaffiliation, tag_id) {
        var tag = {
            'code': $scope.code_new,
            'structure_affiliation': $scope.structureaffiliation,
            'structure_id': $scope.structure_id
        }
        if ($scope.tag_id)
            tag['pk'] = $scope.tag_id;
        $http.post(BASE_URL + 'tags_structure/', tag).then(function success_response(response) {
            $scope.modalMMT($scope.userMMTag);
        },
            function error_response(error_response) {
                if (error_response.status === 401) {
                    window.location.href = "#/";
                    return;
                }
                alert(error_response.data.detail)
            });
    }

    $scope.generatePDF = function () {
        $scope.list = []

        var dd = {
            pageOrientation: 'landscape',
            content: [
                { text: 'Lista Affiliati:', fontSize: 14, bold: true, margin: [0, 20, 0, 20] },
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
                    [{ text: 'Nome Affiliato', style: 'tableHeader', alignment: 'center' }, { text: 'Email', style: 'tableHeader', alignment: 'center' }, { text: 'Tag Struttura', style: 'tableHeader', alignment: 'center' }],
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
/*    $scope.editProfile1 = function (ev) {
        console.log("EDIT!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        $scope.showEditProfile(ev, $scope.profile, $scope.attributeValues);
    }*/
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
    $scope.user_id = 0;
    $scope.modalSerials = function (user_id) {
        $scope.model = {}
        if (user_id)
            $scope.user_id = user_id
        $http.get(BASE_URL + 'COC/serial/list/?user_id=' + user_id + '&structure_id=' + $scope.structure_id).then(
            function success_reponse(response) {
                $scope.serials = response.data;
                $scope.model['start_date_validation'] = new Date()
                angular.forEach($scope.serials, function (serial) {
                    var start = serial.start_date_validation;
                    var end = moment(serial.start_date_validation).add(serial.duration, 'M')
                    serial.end_date_validation = moment(serial.start_date_validation).add(serial.duration, 'M').format('DD/MM/YYYY')
                    serial.start_date_validation = moment(serial.start_date_validation).format('DD/MM/YYYY')
                    $scope.model['start_date_validation'] = new Date(moment.max($scope.model['start_date_validation'], end))
                },
                    function error_response() {
                        alert("Non è stato possibile ottenere la lista dei suoi seriali. Ricaricare la pagina e riprovare");
                        return;
                    })
            });
        $scope.initSerials();
        $("#modal_add_serial").modal('hide')
        $('#modal_serialsCOC').modal('show')
    }
    $scope.newSerial = function () {
        $('#modal_serialsCOC').modal('hide')
        $("#modal_add_serial").modal('show')
    }
    $scope.closeModalAddSerial = function () {
        $("#modal_add_serial").modal('hide')
        $('#modal_serialsCOC').modal('show')
    }
    $scope.editSerial = function () {
        $scope.model.start_date_validation = moment($scope.model.start_date_validation).format('YYYY-MM-DD')
        $http.post(BASE_URL + 'COC/serial/create/?user_id=' + $scope.user_id + '&structure_id=' + $scope.structure_id, $scope.model).then(
            function success_response(response) {
                $scope.modalSerials($scope.user_id);
                $scope.model = {};
            },
            function error_response(response) {
                alert("seriale immesso non valido")
                return;
            });
    }
});
