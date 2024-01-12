myMedBookController.controller('agendaController', function ($scope, $http, $stateParams, $compile, $timeout, $q, OAuthToken) {
  var date = new Date();
  var d = date.getDate();
  var m = date.getMonth();
  var y = date.getFullYear();

  $(".mmb_menu").removeClass('mmb_selected');
  $(".mmb_agenda").addClass('mmb_selected');

  $scope.init = function () {
    $http.get(BASE_URL + "event_type/").then(function successCallback(response) {
      $scope.tipologie_eventi = response.data;
      agenda_schema[0].items[6].options = response.data;
    })
    $scope.callRows('GET', "circle", '/', {}, function (response) {
      agenda_schema[0].items[7].options = response;
    });
    $scope.callRows('GET', "dossier", '/', {}, function (response) {
      agenda_schema[0].items[8].options = response;
    });
    $http.post(BASE_URL + 'devices/checkNotificationAsRead/', { 'item_idx': [], 'item_type': 'event' }).then(
      function () {
        $http.get(BASE_URL + 'devices/notifications/').then(function (response) {
          $scope.notifications = response.data;
        });
      }
    )
  }
  /*$scope.$watchGroup(['terapie','eventi'],function(newValue, oldValue){
    if(oldValue){
      var index = $scope.indexElementInVector(oldValue,$scope.events);
      $scope.events[index] = newValue;
    }
    else{
      $scope.events.push(newValue);
    }
  });*/

  //click sopra l'evento, apre il dettaglio
  $scope.alertOnEventClick = function (date, jsEvent, view) {
    var schema = agenda_schema
    var data = date.object
    if (date.title_object === "therapy") {
      schema = terapia_schema;
    }
    else{
      $http.get(BASE_URL+'event/'+date.object.pk+'/').then(function(response){
        data = response.data
      })
    }
    $scope.showDialogDetail(jsEvent, schema, data, function () {
      $scope.assignEvent();
    });
  };
  //caso in cui sposto un evento deve aggiornare la lista eventi con la nuova data
  $scope.alertOnDrop = function (event, delta, revertFunc, jsEvent, ui, view) {

    if (event.title_object)
      object_type = event.title_object;

    var object_type = "event";

    var dataI = moment(event._start._d).format("YYYY-MM-DDTHH:mm:ssZ");
    var event_values = {
      "start_date": dataI,
    }
    if (event._end)
      event_values["end_date"] = moment(event._end._d).format("YYYY-MM-DDTHH:mm:ssZ");

    if (event.title_object === "therapy") {
      object_type = "therapy";
      event_values.start_date = moment(dataI).format("YYYY-MM-DD")
      if (event._end)
        event_values["end_date"] = moment(event._end._d).format("YYYY-MM-DD");
    }
    $scope.callRows('PUT', object_type, "/" + event.id + "/", event_values, function (response) {
      $scope.assignEvent();
    });
  };
  /* alert on Resize */
  $scope.alertOnResize = function (event, delta, revertFunc, jsEvent, ui, view) {
    alert('Event Resized to make dayDelta ' + delta);
  };
  /* add and removes an event source of choice */
  $scope.addRemoveEventSource = function (sources, source) {
    var canAdd = 0;
    angular.forEach(sources, function (value, key) {
      if (sources[key] === source) {
        sources.splice(key, 1);
        canAdd = 1;
      }
    });
    if (canAdd === 0) {
      sources.push(source);
    }

  };
  /* add custom event*/
  $scope.addEvent = function ($event) {
    $scope.showEditNew($event, agenda_schema, "Crea", null, function () {
      $scope.events.push($scope.model_submit);
      $scope.assignEvent();
    });

  };
  /* remove event */
  $scope.remove = function (index) {
    $scope.events.splice(index, 1);
  };
  /* Change View */
  $scope.changeView = function (view, calendar) {
    uiCalendarConfig.calendars[calendar].fullCalendar('changeView', view);
  };
  /* Change View */
  $scope.renderCalender = function (calendar) {
    if (uiCalendarConfig.calendars[calendar]) {
      uiCalendarConfig.calendars[calendar].fullCalendar('render');
    }
  };

  /* config object */
  $scope.uiConfig = {
    calendar: {
      height: 450,
      //editable: true,
      editable: true,
      firstDay: 1,
      header: {
        left: 'title',
        center: '',
        right: 'today prev,next',
      },
      buttonText: {
        today: 'Oggi'
      },
      monthNames: ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"],
      dayNames: ["Domenica", "Lunedi", "Martedi", "Mercoledi", "Giovedi", "Venerdi", "Sabato"],
      dayNamesShort: ["Dom", "Lun", "Mar", "Mer", "Gio", "Ven", "Sab"],
      eventClick: $scope.alertOnEventClick,
      eventDrop: $scope.alertOnDrop,
      eventResize: $scope.alertOnResize,
      eventRender: function (event, element) {
        element.find('.fc-event-title').css({ textOverflow: 'ellipsis', whiteSpace: 'nowrap', overflow: 'hidden', width: 'inherit', display: 'block' });
        element.attr('title', moment(event.start).format("HH:mm") + " " + event.title);
      },
      timeFormat:'HH:mm'
    }
  };
  //calendario nel menu, non può droppare e si devono vedere i tooltip
  $scope.uiConfig1 = {
    calendar: {
      height: 450,
      editable: false,
      firstDay: 1,
      header: {
        left: 'title',
        center: '',
        right: 'today prev,next',
      },
      buttonText: {
        today: 'Oggi'
      },
      monthNames: ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"],
      dayNames: ["Domenica", "Lunedi", "Martedi", "Mercoledi", "Giovedi", "Venerdi", "Sabato"],
      dayNamesShort: ["Dom", "Lun", "Mar", "Mer", "Gio", "Ven", "Sab"],
      eventClick: $scope.alertOnEventClick,
      eventResize: $scope.alertOnResize,
      eventRender: function (event, element) {
        element.find('.fc-event-title').css({ textOverflow: 'ellipsis', whiteSpace: 'nowrap', overflow: 'hidden', width: 'inherit', display: 'block' });
        element.attr('title', moment(event.start).format("HH:mm") + " " + event.title);
      },
      timeFormat:'HH:mm'
    }
  };
});