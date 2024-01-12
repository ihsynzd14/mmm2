myMedBookController.controller('generalController', function ($scope, $http, $stateParams, $mdDialog, $cookies, Upload, $timeout, $interval, $compile,
    OAuth, OAuthToken, $q, $window, $location) {
    $scope.events = [];
    $scope.modelProfile = { 'email': '' };
    $scope.eventSources = [$scope.events];
    $scope.path = $location.$$path;
    $scope.structure_id = null;
    $scope.input_blocked = true;
    $scope.BASE_PATH = URL_AUTH;
    $scope.checked = []

    /**NOTIFICHE */
    $interval(function () {
        return;
        if ($scope.profile && $scope.profile.is_staff === false) {
            $http.get(BASE_URL + 'devices/notifications/').then(function (response) {
                $scope.notifications = response.data;
            })
        }
    }, 5000);


    $scope.hasPermission = function (type) {
        if ($scope.profile.groups.length <= 0)
            return false;

        $scope.profile.groups.forEach(function (group) {
            if (listLabelGroups[type] == group)
                return true;
        });
        return false;
    }
    $scope.checkifSalvavita = function (name) {
        name = lowercase(name)
        console.log(name)
        if (name.indexOf('salvavita') <= 0)
            return true;
        return false
    }
    $scope.checkRolesStructures = function (group, type) {
        if (!group)
            return true;
        if (type === 'dipendenti' && (group.indexOf('direttore')) >= 0)
            return true;
        if (type === 'ospiti' && (group.indexOf('animatore') >= 0 ||
            group.indexOf('operatore_sanitario') >= 0 ||
            group.indexOf('direttore') >= 0 ||
            group.indexOf('portiere') >= 0))
            return true;
        if (type === 'allarmi' &&
            (group.indexOf('operatore_sanitario') >= 0 ||
                group.indexOf('direttore') >= 0 ||
                group.indexOf('portiere') >= 0))
            return true;
        if ((type === 'bacheca' || type == 'gruppi') &&
            (group.indexOf('animatore') >= 0 ||
                group.indexOf('URP') ||
                group.indexOf('direttore') >= 0))
            return true;
        if ((type === 'actionAffiliatiCOC') &&
            (group.indexOf('portiere') >= 0))
            return false;
        if ((type === 'affiliatiCOC' || type === 'assistenzeCOC') &&
            group.indexOf('operatore_coc') >= 0)
            return true;
        if (group.indexOf('admin_coc') >= 0)
            return true;
        return false;
    }

    //CHIAMATA GENERICA
    $scope.callRows = function (method, table, query_string, body, callback) {
        var p = $http({
            method: method,
            url: BASE_URL + table + query_string,
            data: body,
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (callback === undefined)
            return p;

        p.then(function successCallback(success_response) {
            callback(success_response.data);
        },
            function errorCallback(error_response) {
                if (error_response.status === 401) {
                    window.location.href = "#/";
                    return;
                }
                alert(error_response.data.detail)
            });
    }
    //DELETE
    $scope.showConfirm = function (event, table, id, callback) {
        var confirm = $mdDialog.confirm()
            .title('Sei sicuro di volerlo cancellare?')
            .textContent('Ricordati che la cancellazione sarà permanente.')
            .ariaLabel('TutorialsPoint.com')
            .targetEvent(event)
            .ok('Si')
            .cancel('No');
        $mdDialog.show(confirm).then(function () {
            if (table === 'conversation') {
                $scope.callRows("POST", "deactivateConversation/", '', { "conversation": id }, function () {
                    $scope.status = 'Cancellazione avvenuta con successo!';
                    if (callback)
                        callback();
                });
            }
            else {
                $scope.callRows("DELETE", table + "/" + id + '/', '', {}, function () {
                    $scope.status = 'Cancellazione avvenuta con successo!';
                    if (callback)
                        callback();
                });
            }
        }, function () {
            $scope.status = 'Hai deciso di conservare il tuo record!';
        });
    };
    //VALIDATE
    $scope.formValidate = function (schema_items, model) {
        var flag = true;
        angular.forEach(schema_items, function (item, idx) {
            if (item['required'] == true && !model[item.id])
                flag = false;
        });
        return flag;
    }
    //LOGOUT
    $scope.logout = function () {
        OAuth.revokeToken().then(function () {
            $scope.profileDetail = {};
            window.location.href = "#/";
        });
    }
    $scope.assignEvent = function () {
        var token = OAuthToken.getToken();
        $scope.events.splice(0, $scope.events.length);
        var request = [];
        request = [
            $http.get(BASE_URL + "therapy/").then(
                function successCallback(response_terapie) {
                    response_terapie.data.forEach(function (item) {
                        var data = {
                            id: item.pk,
                            title: item.drug,
                            start: moment(item.start_date).toDate(),
                            allDay: true,
                            className: ['evento_T'],
                            title_object: 'therapy',
                            object: item
                        }
                        if (item.end_date)
                            data['end'] = moment(item.end_date).toDate()
                        $scope.events.push(data);
                    });
                },
                function errorCallback(error_response) {
                    if (error_response.status === 401) {
                        window.location.href = "#/";
                        return;
                    }
                    alert(error_response.data.detail)
                }
            ),
            $http.get(BASE_URL + "event/").then(function successCallback(response_eventi) {
                if (response_eventi && response_eventi.data.length >= 0) {
                    response_eventi.data.forEach(function (item) {
                        //concateno la data e l'orario
                        if (item.event_type) {
                            className = 'evento_' + item.event_type.symbol,
                                $scope.events.push({
                                    id: item.pk,
                                    title: item.name + "(" + item.user.email + ")",
                                    start: moment(item.start_date).toDate(),
                                    end: moment(item.end_date).toDate(),
                                    allDay: false,
                                    className: [className],
                                    object: item
                                });
                        }
                    });
                }
            },
                function errorCallback(error_response) {
                    if (error_response.status === 401) {
                        window.location.href = "#/";
                        return;
                    }
                    alert(error_response.data.detail)
                })
        ]

        $q.all(request);
    }
    //LISTA files
    $scope.getFiles = function (id_dossier) {
        $scope.callRows('GET', "document", "/?dossier=" + id_dossier, {}, function (response) {
            angular.forEach(response, function (item, idx) {
                item.path = URL_FILES + item.path;
                if (idx == (response.length - 1)) {
                    $scope.files_load = response;
                }
            });
        });
    }

    //UPLOAD FILE
    $scope.closeModalUpload = function () {
        $("#modal_upload").modal("hide");
    }
    $scope.uploadAvatar = function () {
        $("#modal_upload").modal("show");
    }
    $scope.usingFlash = FileAPI && FileAPI.upload != null;
    $scope.invalidFiles = [];

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

    $scope.uploadPic = function (file) {
        Upload.http({
            url: BASE_URL + 'upload/profile/avatars/',
            headers: {
                'Content-Type': file.type,
                'Content-Disposition': "inline; filename*=UTF-8''" + encodeURI(file.name)
            },
            data: file
        }).then(function (response) {
            $timeout(function () {
                $scope.closeModalUpload();
                window.location.reload();
            }, 500);
        }, function (response) {
            if (response.status > 0)
                $scope.errorMsg = response.status + ': ' + response.data;
        });
    }
    $scope.uploadFilesDossier = function (file, model, callback) {
        if (!file)
            return;
        Upload.http({
            url: BASE_URL + 'upload/dossier/' + $scope.model.id_familiare + '/',
            method: 'POST',
            headers: {
                'Content-Type': file.type,
                'Content-Disposition': "inline; filename*=UTF-8''" + encodeURI(file.name)
            },
            data: file
        }).then(function (response) {
            $timeout(function () {
                callback();
            }, 500);

        }, function (response) {
            if (response.status > 0)
                $scope.errorMsg = response.status + ': ' + response.data;
        });
    }
    $scope.uploadFilesTherapy = function (file, model, callback) {
        if (!file)
            return;
        Upload.http({
            url: BASE_URL + 'upload/therapy/?pk=' + model.pk,
            method: 'POST',
            headers: {
                'Content-Type': file.type,
                'Content-Disposition': "inline; filename*=UTF-8''" + encodeURI(model.name)
            },
            data: file
        }).then(function (response) {
            $timeout(function () {
                callback();
            }, 500);

        }, function (response) {
            if (response.status > 0)
                $scope.errorMsg = response.status + ': ' + response.data;
        });
    }

    $scope.uploadFilesEvent = function (file, model, callback) {
        if (!file)
            return;
        Upload.http({
            url: BASE_URL + 'upload/events/?pk=' + model.pk,
            method: 'POST',
            headers: {
                'Content-Type': file.type,
                'Content-Disposition': "inline; filename*=UTF-8''" + encodeURI(file.name)
            },
            data: file
        }).then(function (response) {
            $timeout(function () {
                callback();
            }, 500);

        }, function (response) {
            if (response.status > 0)
                $scope.errorMsg = response.status + ': ' + response.data;
        });
    }

    //DIALOG DETTAGLI GENERICA: dialog generica per la visualizzazione dei dettagli
    $scope.showDialogDetail = function (ev, schema, obj, callback) {
        if (!obj)
            obj = {};
        $scope.schema = schema[0];
        $scope.obj_schema = schema;
        $scope.object = angular.copy(obj);
        $scope.callback = callback;
        var query_string = "";
        var current_date = new Date();
        if ($scope.schema.object == 'event') {
            if ($scope.object.start_date)
                $scope.object['start_hour'] = $scope.splitHour($scope.object.start_date);
            else
                $scope.object['start_hour'] = "00:00";
            if ($scope.object.end_date)
                $scope.object['end_hour'] = $scope.splitHour($scope.object.end_date);
            else
                $scope.object['end_hour'] = "01:00";
        }
        if ($scope.object.start_date)
            $scope.object.start_date = moment($scope.object.start_date).format("DD/MM/YYYY");
        if ($scope.object.end_date)
            $scope.object.end_date = moment($scope.object.end_date).format("DD/MM/YYYY");
        if ($scope.object.birthday)
            $scope.object.birthday = moment($scope.object.birthday).format("DD/MM/YYYY");
        if ($scope.object.circleaffiliation_set && $scope.object.circleaffiliation_set.length > 0) {
            angular.forEach($scope.object.circleaffiliation_set, function (item, index) {
                var tmp = { 'email': item.email };
                $scope.object.circleaffiliation_set[index] = tmp;
            });
        }

        $mdDialog.show({
            controller: function () {
                /*$scope.hide = function () {
                    $mdDialog.hide();
                };*/
                $scope.openFile = function (file_path) {
                    window.open(URL_IMAGE + file_path, '_blank');
                }
                $scope.cancel = function () {
                    $mdDialog.cancel();
                    document.getElementById('inputDialog').click();
                    if (callback)
                        callback();
                };
                $scope.deleteDocument = function (ev, document_pk) {
                    $scope.showConfirm(ev, 'document', document_pk, function () {
                        $('#file_' + document_pk).hide()
                        if (callback)
                            callback();
                    })
                }
                $scope.delete_elem = function (ev, id) {
                    $scope.showConfirm(ev, $scope.schema.object, $scope.object.pk, function () {
                        if (callback)
                            callback();
                    });
                }
                $scope.edit = function (ev) {
                    $scope.showEditNew(ev, $scope.obj_schema, 'Modifica', obj, function () {
                        if ($scope.obj_schema.object !== 'events' || $scope.obj_schema.object !== 'therapy') {
                            $scope.callRows("GET", $scope.schema.object + "/" + $scope.object.pk + "/", query_string, {}, function (response) {
                                $scope.showDialogDetail(ev, $scope.obj_schema, response, function () {
                                    if (callback)
                                        callback();
                                });
                            });
                        };
                    });
                }
            },
            templateUrl: 'templates/dialogShowDetail.html',
            parent: angular.element(document.body),
            targetEvent: ev,
            scope: $scope,
            preserveScope: true,
            clickOutsideToClose: true,
            fullscreen: $scope.customFullscreen // Only for -xs, -sm breakpoints.
        }).then(function (answer) {
            if (callback)
                callback();
        });
    }
    $scope.calcBMI = function (peso, altezza) {
        if (!peso || !altezza)
            return null;
        var h = parseInt(altezza) / 100;
        var bmi = Math.pow(h, 2);
        bmi = parseInt(peso) / bmi;
        bmi = bmi.toFixed(2);
        return bmi;
    }
    // DIALOG MODIFICA E CREAZIONE generica
    $scope.showEditNew = function (ev, schema, action, obj, callback, id_esterno) {
        $scope.schema = schema[0];
        $scope.object = obj;
        $scope.action = action;
        $scope.MAX_MULTIPLE_INPUT = MAX_MULTIPLE_INPUT;
        //timepicker
        $scope.hstep = 1;
        $scope.mstep = 15;
        $scope.options = {
            hstep: [1, 2, 3],
            mstep: [1, 5, 10, 15, 25, 30]
        };

        $scope.ismeridian = true;
        //fine timepicker
        $scope.$watch("model.start_hour", function () {
            $scope.model.end_hour = moment($scope.model.start_hour).add(1, 'h');
        });
        $scope.$watch("model.start_date", function () {
            if(!$scope.model.end_date || moment($scope.model.end_date).isBefore($scope.model.start_date))
                $scope.model.end_date = moment($scope.model.start_date).format('YYYY-MM-DD');
        });


        if (action === "Crea" || action === "Aggiungi") {
            $scope.model = {};
            if ($scope.schema.object === "circle") {
                if (!$scope.model.circleaffiliation_set || $scope.model.circleaffiliation_set.length <= 0) {
                    $scope.model.circleaffiliation_set = [{ 'email': '' }];
                }
            }
            var current_date = new Date();
            if ($scope.schema.object === "therapy") {
                $scope.model.posologiestherapy_set = [{ hour: null, posology: '' }];
            }
            if ($scope.schema.object === "files") {
                $scope.model.id_familiare = id_esterno;
            }
            //inizializzazione orari e date
            $scope.schema.items.forEach(function (item) {
                if (item.label === 'start_hour')
                    $scope.model.start_hour = moment();
                if (item.label === 'end_hour')
                    $scope.model['end_hour'] = moment().add(1, 'h');
                if (item.label === 'start_date')
                    $scope.model.start_date = moment().format('YYYY-MM-DD')
                //new Date();
                if (item.label === 'end_date')
                    $scope.model.end_date = moment().format('YYYY-MM-DD')
                //new Date();
                if (item.label === 'birthday') {
                    $scope.model.birthday = new Date();
                }
            });
        }
        if (action === "Modifica") {
            //devo convertire le date da stringa a tipo date
            $scope.model = angular.copy(obj);
            var current_date = new Date();
            if ($scope.schema.object === "event") {
                if ($scope.model.dossier && $scope.model.dossier.pk) {
                    $scope.model.dossier = $scope.model.dossier.pk
                }
                if ($scope.model.event_type)
                    $scope.model.event_type = $scope.model.event_type.pk;
                if ($scope.model.start_date) {
                    var date = $scope.model.start_date.split("/").reverse().join("-");
                    $scope.model['start_hour'] = moment($scope.splitHour($scope.model.start_date), 'HH:mm');
                    $scope.model.start_date = moment(date).format('YYYY-MM-DD')
                } else {
                    $cope.model['start_hour'] = moment("00:00", 'HH:mm');
                    $scope.model.start_date = moment().format('YYYY-MM-DD')
                } if ($scope.model.end_date) {
                    var date = $scope.model.end_date.split("/").reverse().join("-");
                    $scope.model['end_hour'] = moment($scope.splitHour($scope.model.end_date), 'HH:mm');
                    $scope.model.end_date = moment(date).format('YYYY-MM-DD')
                } else {
                    $scope.model['end_hour'] = moment("01:00", 'HH:mm');
                    $scope.model.end_date = $scope.model.start_date
                }
            }
            if ($scope.schema.object === "therapy") {
                if ($scope.model.start_date) {
                    var date = $scope.model.start_date.split("/").reverse().join("-");
                    $scope.model.start_date = moment(date).format('YYYY-MM-DD')
                } else {
                    $scope.model.start_date = moment().format('YYYY-MM-DD')
                }
                if ($scope.model.end_date) {
                    var date = $scope.model.end_date.split("/").reverse().join("-");
                    $scope.model.end_date = moment(date).format('YYYY-MM-DD')
                } else {
                    $scope.model.end_date = $scope.model.start_date
                }
            }
            if ($scope.model.posologiestherapy_set) {
                $scope.model.posologiestherapy_set.forEach(function (item) {
                    item.hour = moment(item.hour, 'HH:mm');
                });
            }
            if ($scope.schema.label == 'dossier_field') {
                $scope.callRows('GET', "circle", '/', {}, function (response) {
                    $scope.schema.items[2].options = response;
                });
            }
            if ($scope.model.hour)
                $scope.model.hour = $scope.timeFromString($scope.model.start_date, $scope.model.hour);
            else
                $scope.model.hour = moment().format('HH:mm');
            if ($scope.schema.object !== "event" && $scope.schema.object !== "therapy") {
                if ($scope.model.start_date)
                    $scope.model.start_date = $scope.dateFromString($scope.model.start_date);
                else
                    $scope.model.start_date = current_date;
                if ($scope.model.end_date)
                    $scope.model.end_date = $scope.dateFromString($scope.model.end_date);
                else
                    $scope.model.end_date = current_date;
                if ($scope.model.birthday)
                    $scope.model.birthday = $scope.dateFromString($scope.model.birthday);
                else
                    $scope.model.birthday = current_date;
            }
        }
        $mdDialog.show({
            controller: function () {
                $scope.disableKey = function (ev) {
                    ev.preventDefault();
                }
                $scope.hide = function () {
                    $mdDialog.hide();
                };
                $scope.cancel = function () {
                    $mdDialog.cancel();
                    document.getElementById('inputDialog').click();
                };
                $scope.answer = function (answer) {
                    $mdDialog.hide(answer);
                    $mdDialog.cancel();
                };
                $scope.saveFile = function (file) {

                    $scope.uploadFilesDossier(file, $scope.model, function () {
                        $scope.hide();
                        $scope.file = null;
                    });
                }
                $scope.saveFileTherapy = function (file, model) {

                    $scope.uploadFilesTherapy(file, model, function () {
                        $scope.hide();
                    });
                }
                $scope.saveFileEvent = function (file, model) {
                    
                    $scope.uploadFilesEvent(file, model, function () {
                        $scope.hide();
                    });
                }
                
                $scope.addNewChoice = function (item, idx) {
                    var values = {}
                    if ($scope.schema.object === 'dossier') {
                        values = { 'email': '' };
                    } else {
                        if (values.hour)
                            values.hour = $scope.timeToString(values.hour);
                        if (values.posology)
                            values.posology = "";
                    }
                    $scope.model[item.label].push(values);
                };

                $scope.removeNewChoice = function (item, idx) {
                    $scope.model[item.label].splice(idx, 1);
                };

                $scope.save = function () {
                    /*if (action === "Modifica" && $scope.model.circle && $scope.model.circle.length > 0)
                        $scope.model.circle.shift()*/
                    $scope.model_submit = angular.copy($scope.model);
                    $scope.file = $scope.model.file;

                    if ($scope.model_submit.posologiestherapy_set) {
                        $scope.model_submit.posologiestherapy_set.forEach(function (item) {
                            if (item.hour)
                                item.hour = $scope.timeToString(item.hour);
                            else
                                delete item;
                        });
                    }
                    if ($scope.model_submit.gruppi_utenti) {
                        $scope.model_submit.gruppi_utenti.forEach(function (item) {
                            item.id_utente = $scope.model_submit.id_utente;
                            if ($scope.model_submit.id)
                                item.id_gruppo = $scope.model_submit.id;
                        });
                    }
                    if ($scope.schema.object === 'event') {
                        if ($scope.model_submit.start_hour && $scope.model_submit.start_date) {
                            $scope.model_submit.start_date = $scope.concatDayHour($scope.model_submit.start_date, $scope.model_submit.start_hour);
                            delete $scope.model_submit.start_hour;
                        }
                        if ($scope.model_submit.end_hour && $scope.model_submit.end_date) {
                            $scope.model_submit.end_date = $scope.concatDayHour($scope.model_submit.end_date, $scope.model_submit.end_hour);
                            delete $scope.model_submit.end_hour;
                        }
                    }
                    else {
                        if ($scope.model_submit.hour)
                            $scope.model_submit.hour = $scope.timeToString($scope.model_submit.hour);
                        if ($scope.model_submit.start_date)
                            $scope.model_submit.start_date = $scope.transformDateToString($scope.model_submit.start_date);
                        if ($scope.model_submit.end_date)
                            $scope.model_submit.end_date = $scope.transformDateToString($scope.model_submit.end_date);
                    }
                    if ($scope.action == "Crea" || $scope.action == "Aggiungi") {
                        /*if (!$scope.formValidate($scope.schema.items, $scope.model_submit))
                            return;
                        else*/
                        $scope.callRows("POST", $scope.schema.object, "/", $scope.model_submit, function (response) {
                            $scope.hide();
                            if ($scope.schema.object === "therapy") {
                                $scope.events.push({
                                    id: response.id,
                                    title: response.drug,
                                    start: moment(response.start_date).toDate(),
                                    end: moment(response.end_date).toDate(),
                                    allDay: true,
                                    className: ['evento_T'],
                                    title_object: 'terapia',
                                    object: response
                                })
                                if ($scope.file)
                                    $scope.saveFileTherapy($scope.file, response)
                            }
                            if ($scope.schema.object === "event" && $scope.file) {
                                $scope.saveFileEvent($scope.file, response)
                            }
                            $scope.model_submit = {};
                        });
                    }
                    if ($scope.action == "Modifica") {
                        /*if (!$scope.formValidate($scope.schema.items, $scope.model_submit))
                            return;
                        else*/

                        $scope.callRows("PUT", $scope.schema.object, "/" + $scope.model_submit.pk + "/", $scope.model_submit, function (response) {
                            $scope.hide();
                            $scope.model_submit = {};
                            if ($scope.schema.object === "therapy") {
                                $scope.assignEvent();
                                if ($scope.file)
                                    $scope.saveFileTherapy($scope.file, response)
                            }
                            if ($scope.schema.object === "event" && $scope.file) {
                                $scope.saveFileEvent($scope.file, response)
                            }
                        });
                    }
                }
                //da stringa a data
                $scope.transformDateFromString = function (date) {
                    return $scope.dateFromString(date);
                }
                //da data a stringa
                $scope.transformDateToString = function (date) {
                    return $scope.formatDateinDB(date);
                }
            },
            templateUrl: 'templates/dialogEditNew.html',
            parent: angular.element(document.body),
            targetEvent: ev,
            scope: $scope,
            preserveScope: true,
            clickOutsideToClose: true,
            fullscreen: $scope.customFullscreen // Only for -xs, -sm breakpoints.
        }).then(function (answer) {
            $scope.model = {};
            if (callback) {
                callback();
            }
        });
    };
    //TOOLTIP
    $scope.demo = {
        showTooltip: false,
        tipDirection: 'right'
    };

    $scope.demo.delayTooltip = undefined;
    $scope.$watch('demo.delayTooltip', function (val) {
        $scope.demo.delayTooltip = parseInt(val, 10) || 0;
    });

    $scope.$watch('demo.tipDirection', function (val) {
        if (val && val.length) {
            $scope.demo.showTooltip = true;
        }
    });

    //GESTIONE DATE
    //da stringa a data
    $scope.dateFromString = function (date) {
        if (!date)
            return null;
        var datefromstring = moment(date, "DD/MM/YYYY");
        return datefromstring.toDate();
    }
    //da data a stringa
    $scope.formatDate = function (date) {
        if (!date)
            return null;
        var date = moment(date).format("DD/MM/YYYY");
        return date;
    }
    //formato in db
    $scope.formatDateinDB = function (date) {
        if (!date)
            return null;
        var date = moment(date).format("YYYY-MM-DD");
        return date;
    }
    //la funzione restituisce true se la data corrente è compresa fra le date passate come parametro, false altrimenti
    $scope.checkCurrentDate = function (start_date, end_date) {
        var end_date1 = moment(end_date, 'DD/MM/YYYY');
        if (moment().isSame(end_date1, 'day') || moment().isBefore(end_date1, 'day'))
            return true;
        return false;
    }
    $scope.checkDifferentBetweenDate = function (date, num_diff) {
        var a = moment();
        var b = moment(date);
        if (moment().diff(b, 'days') <= num_diff)
            return true;
        return false;
    }
    $scope.dateBefore = function (dateI, dateF) {
        if (!dateI || !dateF)
            return false;
        var a = moment(dateI, 'DD/MM/YYYY');
        var b = moment(dateF, 'DD/MM/YYYY');
        if (a.isBefore(b))
            return true;
        return false;
    }
    // La funzione concatena un giorno (YYYY-MM-DD) con un orario (HH:mm)
    $scope.concatDayHour = function (data, orario) {
        if (!orario)
            return data;
        hour = moment(orario).format("HH:mm:ss")
        var data_res = moment(data).format("YYYY-MM-DD");
        var concat_date_hour = data_res + "T" + hour + ".000Z"
        var result = moment(concat_date_hour)._d;
        return result;
    }
    $scope.splitHour = function (data) {
        if (!data)
            return;
        var hour = moment(data).format('HH:mm');
        return hour;
    }
    //orario: ha bisogno anche della data per poterlo tramutare in Date, la libreria parsa in automatico 
    $scope.timeFromString = function (gg, time) {
        var date = $scope.concatDayHour(gg, time);
        return moment(date).toDate();
    }
    $scope.timeToString = function (time) {
        return moment(time).format("HH:mm");
    }

    //funzione che restituisce l'indice del vettore dove si trova l'occorrenza dell'id passato'
    $scope.indexElementInVector = function (id_terapy, vector) {
        var index = -1;
        angular.forEach(vector, function (item, idx) {
            if (id_terapy === item.id)
                index = idx;
        });
        return index;
    }

    //INIT PROFILO
    $scope.reloadProfilo = function (callback) {
        $(".benvenutoAdmin").hide();
        $(".menu-laterale").show();
        $(".container .menu .menu_init").show();
        $(".menu-utenti").css("display", "none !important");

        var request = [
            $http.get(BASE_URL + "profile/").then(function successCallback(response) {
                $scope.profile = response.data;
                if ($scope.profile.avatar)
                    $scope.profile.avatar = URL_IMAGE + $scope.profile.avatar;
                else
                    $scope.profile.avatar = IMG_DEFAULT;
                if ($scope.profile.is_staff === true)
                    return;
            }).then(function () {
                if($scope.profile.is_staff===true){
                    return;
                }
                $http.get(BASE_URL + "circle/").then(function (response) {
                    $scope.gruppi = response.data;
                });
            }),
            $http.get(BASE_URL + "event_type/").then(function successCallback(response) {
                $scope.tipologie_eventi = response.data;
            })
        ]
        $q.all(request);
    }

    $scope.init = function () {
        $scope.position();
        $scope.profileDetail = [];
        $scope.eventi = [];
        $scope.reloadProfilo();
    };

    //utenti
    $scope.openTableUsers = function (page) {
        if (!page)
            page = 1;
        $scope.currentPage = page;
        $(".paginate_button").removeClass("active");
        $("#range_" + $scope.currentPage).addClass("active");
        $scope.callRows('GET', "utenti/all?page=" + page + "&per_page=" + PAGE_LIMIT + "&sort=createdAt DESC", "", {}, function (response) {
            $scope.users = response.data;
            $scope.totalItems = response.meta.total;
            $scope.total_page = response.meta.pageCount;

            $(".container_table_users").show();
        })
    }

    $scope.position = function () {
        var tmp = $window.location.href;
        tmp = tmp.split("#");

        if (tmp === "/admin") {
            $(".menu_utenti").css("display", "block !important");
            $(".menu_utenti").show();
        }
        else {
            if (tmp === "/profilo") {
                $window.location.href = "#/profilo";
            }
            $(".container .menu .menu_utenti").css("display", "none !important");
            $(".container .menu .menu_utenti").hide();
            $(".benvenutoAdmin").hide();
            $(".menu-laterale").css("display", "block !important");
            $(".menu-laterale").show();
            $(".user .benvenuto").css("display", "block !important");
            $(".user .benvenuto").show();
            $(".fa-sign-out").show();
            $(" .fa-envelope").show();
            $(".fa-bell").show();
            $(".container .menu .menu_init").show();
            $(".container .menu .menu_init").css("display", "block !important");
        }
    }

    $scope.openAlarm = function () {
        window.open(
            $location.$$absUrl.replace($location.$$path, 'allarmi'),
            '_blank' // <- This is what makes it open in a new window.
        );
        $scope.path = $location.$$path;
    }
    $scope.openAssistenzaCOC = function () {
        window.open(
            $location.$$absUrl.replace($location.$$path, 'gestioneRichiesteCOC'),
            '_blank' // <- This is what makes it open in a new window.
        );
        $scope.path = $location.$$path;
    }

    $scope.showEditProfile = function (ev, profile, attributeValues, callback) {
        $scope.saveEnabled = false;
        $scope.schemaProfile = schemaProfile;
        $scope.modelProfile = profile;
        $scope.modifiedModels = [];
        $scope.modelCOC = [];
        //Se non fosse indicata la data di nascita allora si deve visualizzare la data odierna
        if ($scope.modelProfile['birthday'])
            $scope.modelProfile['birthday'] = moment($scope.modelProfile['birthday']).format('YYYY-MM-DD');
        if (!$scope.modelProfile['birthday'])
            $scope.modelProfile['birthday'] = moment().format('YYYY-MM-DD')

        $scope.attributeValues = attributeValues;

        $mdDialog.show({
            controller: function () {
                $scope.hide = function () {
                    $mdDialog.hide();
                };
                $scope.cancel = function () {
                    $mdDialog.cancel();
                    document.getElementById('inputDialog').click();
                };
                $scope.disableKey = function (ev) {
                    ev.preventDefault();
                }
                $scope.save = function () {
                    if ($scope.path.indexOf('COC') >= 0) {
                        $scope.submit = [];
                        var lifesaver = $scope.modelProfile.lifesaver
                        angular.forEach($scope.attributeValuesCOC, function (attribute_group) {
                            angular.forEach(attribute_group.attributes, function (attribute) {
                                if (!attribute.value || attribute.value.length <= 0 || (attribute.attribute.datatype!=='boolean' && attribute.value == false))
                                    return;
                                if (lifesaver === attribute.pk) {
                                    lifesaver = attribute;
                                }
                                $scope.submit.push(attribute)
                            });
                        })
                        querystring = '?guest_id=' + $scope.profile.pk + '&coc_request_action=' + $cookies.get('structure_id')

                        $scope.callRows("PUT", "COC/profile/editattributes", "/" + querystring, { data: $scope.submit }).then(function () {
                            $mdDialog.hide();
                            /*$http.get(BASE_URL + 'COC/attribute/values/').then(function success_response(response) {
                                angular.forEach(response.data, function (attributevalues, idx) {
                                    angular.forEach(attributevalues.attributes, function (item) {
                                        if (item && lifesaver && item.attribute && lifesaver.attribute && lifesaver.attribute.name === item.attribute.name) {
                                            $scope.modelProfile.lifesaver = item.pk;
                                        }
                                        if (idx >= response.data.length - 1) {
                                            $mdDialog.hide();
                                            $scope.model_submit = {};
                                        }
                                    });
                                });
                                $scope.callRows("PUT", "profile/edit", "/" + querystring, { data: $scope.modelProfile }).then(function (response) {
                                    $scope.modelProfile = {};
                                    $scope.profile = response.data;
                                    if ($scope.profile.avatar)
                                        $scope.profile.avatar = URL_IMAGE + $scope.profile.avatar;
                                    else
                                        $scope.profile.avatar = IMG_DEFAULT;
                                    if ($scope.profile.is_staff === true)
                                        return;
                                });
                                $mdDialog.hide();
                            });*/
                        });
                    }
                    else {
                        $scope.submit = [];
                        var lifesaver = $scope.modelProfile.lifesaver
                        angular.forEach($scope.attributeValues, function (attribute_group) {
                            angular.forEach(attribute_group.attributes, function (attribute) {
                                if (!attribute.value || attribute.value.length <= 0 || (attribute.attribute.datatype!=='boolean' && attribute.value == false))
                                    return;
                                console.log(attribute.attribute.pk)
                                if (lifesaver === attribute.pk) {
                                    lifesaver = attribute;
                                }
                                $scope.submit.push(attribute)
                            });
                        })
                        if ($scope.modelProfile['birthday'])
                            $scope.modelProfile['birthday'] = moment($scope.modelProfile['birthday']).format("YYYY-MM-DD");

                        /* if ($scope.modelProfile.pk != $scope.profile.pk) {*/
                        var querystring = '?guest_id=' + $scope.modelProfile.pk
                        /*} */
                        $scope.callRows("PUT", "profile/editattributes", "/" + querystring, { data: $scope.submit }).then(function () {
                            $http.get(BASE_URL + 'attribute/values/').then(function success_response(response) {
                                angular.forEach(response.data, function (attributevalues, idx) {
                                    angular.forEach(attributevalues.attributes, function (item) {
                                        if (item && lifesaver && item.attribute && lifesaver.attribute && lifesaver.attribute.name === item.attribute.name) {
                                            $scope.modelProfile.lifesaver = item.pk;
                                        }
                                        if (idx >= response.data.length - 1) {
                                            $scope.callRows("PUT", "profile/edit", "/" + querystring, { data: $scope.modelProfile }).then(function (response) {
                                                $mdDialog.hide();
                                                $scope.model_submit = {};
                                                $scope.modelProfile = {};
                                                $scope.profile = response.data;
                                                if ($scope.profile.avatar)
                                                    $scope.profile.avatar = URL_IMAGE + $scope.profile.avatar;
                                                else
                                                    $scope.profile.avatar = IMG_DEFAULT;
                                                if ($scope.profile.is_staff === true)
                                                    return;
                                            });
                                        }
                                    });
                                });
                                $scope.saveActionCOC();
                            });

                        });

                    }
                }
            },
            templateUrl: 'templates/overlay_edit_profile.html',
            parent: angular.element(document.body),
            targetEvent: ev,
            scope: $scope,
            preserveScope: true,
            clickOutsideToClose: true,
            fullscreen: $scope.customFullscreen // Only for -xs, -sm breakpoints.
        }).then(function () {
            $scope.model = {};
            console.log("edit finito")
            if (callback) {
                callback();
            }
        });
    }
    $scope.openFile = function (file_path) {
        window.open(URL_IMAGE + file_path, '_blank');
    }

    $scope.openDialogPrivacy = function () {
        $("#modal_privacy").modal("show");
    }

    $scope.closeDialogPrivacy = function () {
        $("#modal_privacy").modal("hide");
    }
    $scope.openPdfManual = function () {
        window.open('documents/Piattaforma_MYMEDBOOK_user_manual.pdf', '_blank');
    }
    $scope.openPdfSmartphoneCompatibility = function () {
        window.open('documents/ELENCO_SMARTPHONE_CON_LETTORI_NFC.pdf', '_blank');
    }

    /*$scope.index_class=0;
    $scope.changeClass = function(){
        $scope.index_class=$scope.index_class+1;
        if($scope.index_class%3==0)
            return "boxmmt3"
        else if ($scope.index_class%3==1)
            return "boxmmt2"
        else
            return "boxmmt1"
    }*/
    $scope.initPost = function () {
        if($scope.profile.is_staff===true){
            return;
        }
        $http.post(BASE_URL + 'devices/checkNotificationAsRead/', { 'item_idx': [], 'item_type': 'posts' }).then(
            function () {
                $http.get(BASE_URL + 'devices/notifications/').then(function (response) {
                    $scope.notifications = response.data;
                    window.location.href = '#/bacheca';
                });
            }
        );
    }
    $scope.initDossier = function () {
        if($scope.profile.is_staff===true){
            return;
        }
        $http.post(BASE_URL + 'devices/checkNotificationAsRead/', { 'item_idx': [], 'item_type': 'dossier' }).then(
            function () {
                $http.get(BASE_URL + 'devices/notifications/').then(function (response) {
                    $scope.notifications = response.data;
                });
            }
        );
        window.location.href = '#/dossier';
    }
    $scope.initGruppi = function () {
        if($scope.profile.is_staff===true){
            return;
        }
        $http.get(BASE_URL + "circle/").then(function (response) {
            $scope.gruppi = response.data;
            $scope.item_idx = [];
            angular.forEach(response.data, function (item) {
                console.log(item.pk)
                $scope.item_idx.push(item.pk)
            });
            $http.post(BASE_URL + 'devices/checkNotificationAsRead/', { 'item_idx': [], 'item_type': 'circle' }).then(
                function () {
                    $http.get(BASE_URL + 'devices/notifications/').then(function (response) {
                        $scope.notifications = response.data;
                    });
                }
            )
        });
    }
    $scope.loadchats = function () {
        if($scope.profile.is_staff===true){
            return;
        }
        $http.post(BASE_URL + 'devices/checkNotificationAsRead/', { 'item_idx': [], 'item_type': 'message' }).then(
            function () {
                $http.get(BASE_URL + 'devices/notifications/').then(function (response) {
                    $scope.notifications = response.data;
                });
            }
        )
        window.location.href = '#/chat';
    }
    $scope.user_aff = null;
    //FUNZIONE DI SALVATAGGIO AZIONI PER COC
    $scope.initCOC = function (user_aff) {
        window.dispatchEvent(new Event('resize'));
        var querystring = '';
        $scope.modelCOC = [];
        if (user_aff) {
            querystring = '?user_id=' + user_aff;
            $scope.user_aff = user_aff;
            if($cookies.get('structure_id')){
                querystring = querystring+'&structure_id=' + $cookies.get('structure_id')
            }
        }
        $scope.textCOC = {
            'call': 'Chiamare un numero scelto',
            'sms': 'Inviare SMS',
            'email': 'Inviare una mail',
            'circle': 'Inviare messaggi ad un gruppo di MMB',
        }
        var request = [
            $http.get(BASE_URL + 'COC/structure/list/' + querystring).then(function (response) {
                $scope.tabs_structure = response.data;
                angular.forEach($scope.tabs_structure, function (tab_structure) {
                    $scope.modelCOC[tab_structure.structure.pk] = []
                    angular.forEach(tab_structure.serials, function (serial) {
                        serial.end_date_validation = moment(serial.start_date_validation).add(serial.duration, 'M').format('DD/MM/YYYY')
                        serial.start_date_validation = moment(serial.start_date_validation).format('DD/MM/YYYY')
                    });
                    angular.forEach(tab_structure.actions, function (action) {
                        if (action.action_type == 'circle') {
                            if (!$scope.modelCOC[tab_structure.structure.pk][action.action_type] || $scope.modelCOC[tab_structure.structure.pk][action.action_type].length <= 0)
                                $scope.modelCOC[tab_structure.structure.pk][action.action_type] = [action.circle];
                            else {
                                $scope.modelCOC[tab_structure.structure.pk][action.action_type].push(action.circle);
                            }
                        } /*if (action.action_type == 'call') {
                            if (!$scope.modelCOC[tab_structure.structure.pk][action.action_type] || $scope.modelCOC[tab_structure.structure.pk][action.action_type].length <= 0)
                                $scope.modelCOC[tab_structure.structure.pk][action.action_type] = [action.value];
                            else {
                                $scope.modelCOC[tab_structure.structure.pk][action.action_type].push(action.value);
                            }
                        } */
                        else
                            $scope.modelCOC[tab_structure.structure.pk][action.action_type] = action.value;
                    });
                });
            }),
            $http.get(BASE_URL + 'COC/attribute/values/' + querystring).then(function success_response(response) {
                $scope.attributeValuesCOC = response.data;
            },
                function error_response(error_response) {
                    if (error_response.status === 401) {
                        window.location.href = "#/";
                        return;
                    }
                    alert(error_response.data.detail)
                }),
            $http.get(BASE_URL + 'attribute/schema/' + querystring).then(function success_response(response) {
                $scope.attributeSchema = response.data;
            },
                function error_response(error_response) {
                    alert(error_response.data.detail)
                }),
        ]
        $q.all(request)
    }
    $scope.checkInp = function (value) {
        console.log(value)
        if (value != '') {
            var regex = /^[0-9]+$/;
            if (value.match(regex) == null) {
                alert('Il campo dev\'essere numerico')
                return;
            }
        }
    }

    $scope.saveActionCOC = function () {
        angular.forEach(Object.keys($scope.modelCOC), function (item) {
            var idx = 0;
            for (var field in $scope.modelCOC[item]) {
                if (field === 'circle') {
                    angular.forEach($scope.modelCOC[item][field], function (circle_id) {
                        body = {
                            'structure': parseInt(item),
                            'action': {
                                'name': $scope.textCOC['circle'],
                                'label': $scope.textCOC['circle'],
                                'action_type': 'circle',
                                'circle': circle_id
                            }
                        }
                        $http.post(BASE_URL + 'COC/actions/create/', body).then(
                            function success_response(response) {
                                $scope.initCOC($scope.user_aff);
                            },
                            function error_response() {
                                alert("Non è stato possibile aggiornare le sue azioni. Riprovare");
                                return;
                            })
                    });
                }
                else {
                    if ($scope.modelCOC[item][field] === "") {
                        $http.delete(BASE_URL + "COC/actions/delete/?action_type=" + Object.keys($scope.modelCOC[item])[idx] + '&structure_id=' + parseInt(item)).then(
                            function success_response(response) {
                                $scope.initCOC($scope.user_aff);
                            },
                            function error_response() {
                                alert("Non è stato possibile aggiornare le sue azioni. Riprovare")
                                return;
                            })
                    } else {
                        body = {
                            'structure': parseInt(item),
                            'action': {
                                'name': $scope.textCOC[Object.keys($scope.modelCOC[item])[idx]],
                                'label': $scope.textCOC[Object.keys($scope.modelCOC[item])[idx]],
                                'action_type': Object.keys($scope.modelCOC[item])[idx],
                                'value': $scope.modelCOC[item][field]
                            }
                        }
                        $http.post(BASE_URL + 'COC/actions/create/', body).then(
                            function success_response(response) {
                                $scope.initCOC($scope.user_aff);
                            },
                            function error_response() {
                                alert("Non è stato possibile aggiornare le sue azioni. Riprovare");
                                return;
                            })

                    }
                }
                idx++;
            }
        })
    }
    $scope.initSerials = function () {
        $scope.allSerials = []
        $http.get(BASE_URL + 'COC/serial/allList/?structure_id=' + $cookies.get('structure_id')).then(
            function success_response(response) {
                angular.forEach(response.data, function (item) {
                    $scope.allSerials.push(item.serial);
                },
                    function error_response() {
                        alert("Non è stato possibile ottenere la lista dei seriali validi. Riprovare");
                        return;
                    })

            });
    }
    var idx = 0;
    $scope.addNewChoiceCircle = function (structure_id) {
        if (!$scope.modelCOC[structure_id]['circle'])
            $scope.modelCOC[structure_id]['circle'] = [''];
        else {
            $scope.modelCOC[structure_id]['circle'].push('');
        }
        idx++;
    };

    $scope.removeNewChoiceCircle = function (structure_id) {
        var lastItem = $scope.modelCOC[structure_id]['circle'].length - 1;
        $scope.modelCOC[structure_id]['circle'].splice(lastItem);
    };

    /*   $scope.addNewChoiceCall = function (structure_id) {
           if (!$scope.modelCOC[structure_id]['call'])
               $scope.modelCOC[structure_id]['call'] = [''];
           else {
               $scope.modelCOC[structure_id]['call'].push('');
           }
       };
   
       $scope.removeChoiceCall = function (structure_id) {
           var lastItem = $scope.modelCOC[structure_id]['call'].length - 1;
           $scope.modelCOC[structure_id]['call'].splice(lastItem);
       };
   
       $scope.addNewChoiceEmail = function (structure_id) {
           if (!$scope.modelCOC[structure_id]['email'])
               $scope.modelCOC[structure_id]['email'] = [''];
           else {
               $scope.modelCOC[structure_id]['email'].push('');
           }
           idx++;
       };

       $scope.removeChoiceEmail = function (structure_id) {
           var lastItem = $scope.modelCOC[structure_id]['email'].length - 1;
           $scope.modelCOC[structure_id]['email'].splice(lastItem);
       };
   */
    $scope.openDetailCOC = function (user_id, ev) {
        if ($scope.profile && $scope.profile.is_staff === true) {
            return;
        }
        $scope.user = user_id;
        $scope.user_aff = user_id;
        $scope.schemaProfile = schemaProfile;
        $scope.checkEditDisabled = true;
        var request = [
            $http.get(BASE_URL + 'user/?structure_id=' + $cookies.get('structure_id') + '&user_id=' + user_id).then(
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
            var querystring = '?code=' + $scope.tag_ospite;
            $scope.initCOC(user_id)
            var request = $http.get(BASE_URL + 'mymedtag/' + querystring).then(function success_response(response) {
                $scope.mymedtag = response.data;
                if ($scope.mymedtag.user.avatar)
                    $scope.mymedtag.user.avatar = URL_IMAGE + $scope.mymedtag.user.avatar;
                else
                    $scope.mymedtag.user.avatar = IMG_DEFAULT;
                $scope.lista = [];
                _($scope.mymedtag.attributes_groups).forEach(function (value) {
                    if (value.attribute.datatype !== 'enum')
                        return;

                    if (($scope.lista.length > 0) && $scope.lista[value.attribute.pk])
                        $scope.lista[value.attribute.pk].value = $scope.lista[value.attribute.pk].value + ', ' + value.value;
                    else
                        $scope.lista[value.attribute.pk] = { 'name': value.attribute.name, 'value': value.value };
                });
            },
                function error_response(error_response) {
                    $scope.mymedtag = {}
                });
        }).then(function () {
            $mdDialog.show({
                controller: function () {
                    $scope.hide = function () {
                        $mdDialog.hide();
                    };
                    $scope.cancel = function () {
                        $mdDialog.cancel();
                        document.getElementById('inputDialog').click();
                    };

                    //DIALOG SALVAVITA: visualizzazione delle informazioni del salvavita
                    $scope.showDialogSalvavita = function (ev) {
                        $scope.URL_IMAGE = URL_IMAGE;
                        $scope.IMG_DEFAULT = IMG_DEFAULT;
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

    $scope.onchangecheckbox = function(attribute){
        if($('.date_with_checkbox_'+attribute.attribute.pk).hasClass('md-checked')){
            $scope.checked[attribute.attribute.pk]=false;
            attribute.value=null
            $('.datecheck_'+attribute.attribute.pk).hide()
            $('.date_with_checkbox_'+attribute.attribute.pk).removeClass('md-checked')
        }
        else{
            $scope.checked[attribute.attribute.pk]=true;
            $('.datecheck_'+attribute.attribute.pk).show()
            $('.date_with_checkbox_'+attribute.attribute.pk).addClass('md-checked')
        }
    }
    $scope.changePathology = function(attribute){
        if (attribute.other.length<=0){
            attribute.value=null;
        }
    }

});
