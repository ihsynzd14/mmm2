myMedBookController.controller('gestioneAllarmiController', function ($scope, $http, $window, $stateParams, $rootScope, $mdDialog, $q, $location, $cookies, $interval) {
    $('.mobile_MMB').hide()
    $('.mobile_CDV').show()
    var structure_id = $cookies.get('structure_id');
    $scope.alarms = [];
    $scope.flag_handled = false;

    // Create a couple of global variables to use.
    var audioElm = document.getElementById("audio1"); // Audio element
    var ratedisplay = document.getElementById("rate"); // Rate display area

    $scope.playAudio = function () {
        audioElm.src = document.getElementById('audioFile').value;
        audioElm.play();
    }
    $scope.pauseAudio = function () {
        audioElm.pause();
    }
    $scope.getAlarms = function (flag) {
        var query_string = ""
        if (flag == false)
            query_string = "&handled=" + flag
        $http.get(BASE_URL + 'alarm/?structure_id=' + structure_id + query_string).then(function successCalback(response) {
            $scope.alarms = response.data;
            if (!flag && $scope.alarms.length > 0) {
                $scope.playAudio(audioElm);
            }
            else {
                $scope.pauseAudio();
            }
            $scope.flag_handled = flag;
            console.log($scope.flag_handled)
        },
            function errorCallback(error_response) {
                if (error_response.status === 401) {
                    window.location.href = "#/";
                    return;
                }
                alert(error_response.data.detail)
            });
    }

    $interval(function () {
        console.log("interval: " + $scope.flag_handled)
        if ($scope.flag_handled)
            $scope.getAlarms(true);
        else
            $scope.getAlarms(false);
    }, 5000);

    $scope.onoffAlarm = function (alarm) {
        $http.post(BASE_URL + 'alarm/toggleactive/?alarm_id=' + alarm.pk, { 'handled': alarm.handled }).then(function successCallback(response) {
            if ($scope.flag_handled)
                $scope.getAlarms(true);
            else
                $scope.getAlarms(false);
        },
            function errorCallback(error_response) {
                if (error_response.status === 401) {
                    window.location.href = "#/";
                    return;
                }
                alert(error_response.data.detail)
            })
    }

    $scope.openOverlayAllarmi = function () {
        $('#modal_search_alarms').modal('show')
    }

    $scope.downloadPDF = function () {
        $scope.list = []
        var querystring = '';
        if (!$scope.date)
            querystring = '?dateI=' + moment().format('YYYY-MM-DD')
        if ($scope.date && $scope.date.start)
            querystring = '?dateI=' + moment($scope.date.start).format('YYYY-MM-DD')
        if ($scope.date && $scope.date.end)
            querystring = querystring + '&dateF=' + moment($scope.date.end).format('YYYY-MM-DD')

        $http.get(BASE_URL + 'alarm/filter/' + querystring).then(function (response) {
            $scope.allAlarm = response.data;
            var dd = {
                pageOrientation: 'landscape',
                content: [
                    { text: 'Lista Allarmi:', fontSize: 14, bold: true, margin: [0, 20, 0, 20] },
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
                    widths: ['*', '*', '*', '*', '*'],
                    body: [
                        [{ text: 'Allarme', style: 'tableHeader', alignment: 'center' }, { text: 'Zona', style: 'tableHeader', alignment: 'center' },
                        { text: 'Data', style: 'tableHeader', alignment: 'center' }, { text: 'Richiedente', style: 'tableHeader', alignment: 'center' },
                        { text: 'Gestito Da', style: 'tableHeader', alignment: 'center' }],
                    ]
                },
                layout: 'lightHorizontalLines'
            }
            angular.forEach($scope.allAlarm, function (alarm, idx) {
                var data = [
                    { 'text': alarm.message, style: 'row', alignment: 'center' },
                    { 'text': alarm.sensor.caption, style: 'row', alignment: 'center' },
                    { 'text': moment(alarm.date).format('DD/MM/YYYY'), style: 'row', alignment: 'center' }
                ]
                if(alarm.caller)
                    data.push({ 'text': alarm.caller.first_name + ' ' + alarm.caller.last_name, style: 'row', alignment: 'center' })
                else
                    data.push({ 'text': '-', style: 'row', alignment: 'center' })
                if (alarm.handler)
                    data.push({ 'text': alarm.handler.first_name + ' ' + alarm.handler.last_name, style: 'row', alignment: 'center' })
                else
                    data.push({ 'text': '-', style: 'row', alignment: 'center' })
                subcontent.table.body.push(data)

                if (idx >= $scope.allAlarm.length - 1) {
                    dd.content.push(subcontent)
                    pdfMake.createPdf(dd).print();
                }
            })
        });
    }
});