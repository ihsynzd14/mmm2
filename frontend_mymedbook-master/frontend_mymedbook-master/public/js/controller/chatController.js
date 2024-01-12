myMedBookController.controller('chatController', function ($scope, $http, $stateParams, $window, $q, $mdDialog, $timeout) {

    $scope.currentpage = 1;
    $('.mobile_MMB').show()
    $('.mobile_CDV').hide()
    $('.mmb_menu').removeClass('mmb_selected')

    $scope.loadchats = function () {
        $scope.URL_IMAGE = URL_IMAGE;
        var request = [$http.get(BASE_URL + 'conversations/withmessages/').then(function success_response(response) {
            $scope.conversations = response.data;
            angular.forEach($scope.conversations, function (item) {
                if (!item.image) {
                    item.image = IMG_DEFAULT;
                }
                else {
                    item.image = URL_IMAGE + item.image;
                }
            });
        }),
        $http.get(BASE_URL + 'users/listForChat/').then(function (response) {
            $scope.allUsers = response.data;
            $scope.allEmails = []
            angular.forEach($scope.allUsers, function (item) {
                $scope.allEmails.push(item.email)
            })
        }),
        $http.post(BASE_URL + 'devices/checkNotificationAsRead/', { 'item_idx': [], 'item_type': 'message' }).then(
            function () {
                $http.get(BASE_URL + 'devices/notifications/').then(function (response) {
                    $scope.notifications = response.data;
                });
            }
        )]
        $q.all(request).then(function () {
            console.log("AUTOCOMPLETE")
            $("#tags").autocomplete({
                source: ['aaaaa']
            });
        })
    }

    $scope.getMessages = function (conv_pk, to_ts, from_ts) {
        if (!to_ts) {
            to_ts = moment().utc().unix();
            var $target = $('#chatbox');
            $target.animate({ scrollTop: $target.height() }, 1000);
        }
        if ($scope.conversation_choise.messages.first.created !== to_ts) {
            $('#reload_messages').show();
            $http.get(BASE_URL + 'messages/?conv_id=' + conv_pk + '&to_ts=' + to_ts + '&limit=10').then(function (response) {
                angular.forEach(response.data, function (item, idx) {
                    item['data_creazione'] = item['created'] * 1000;
                    $scope.messages.unshift(item);
                });
                $scope.first_message = $scope.messages[0];
                if ($scope.conversation_choise.messages.first.created == $scope.messages[0].created) {
                    $('#reload_messages').hide();
                }
            });
        }
    }
    $scope.conferma = function (ev, id) {
        $scope.showConfirm(ev, 'conversation', id, function () {
                $scope.loadchats();
        });
      }
    $scope.openConversation = function (conv) {
        $scope.conversation_choise = conv;
        $scope.messages = [];
        $scope.getMessages(conv.pk, null)
        $('#modal_view_conversation').modal('show');
    }

    $scope.overlayNewConversation = function () {
        $scope.model = {}
        $('#modal_new_conversation').modal('show');
    }

    $scope.ngModelOptionsSelected = function (value) {
        if (arguments.length) {
            _selected = value;
        } else {
            return _selected;
        }
    };

    $scope.modelOptions = {
        debounce: {
            default: 500,
            blur: 250
        },
        getterSetter: true
    };

    $scope.createConversation = function () {
        $scope.model['message'] = {
            'text': $scope.text
        }
        console.log($scope.model)
        console.log($scope.profile.pk)
        $http.post(BASE_URL + 'conversation/', $scope.model).then(function (response) {
            $('#modal_new_conversation').modal('hide');
            $scope.text = '';
            $scope.loadchats(1)
        })
    }

    $scope.sendMessage = function (conversation) {
        var data = {
            conversation: $scope.conversation_choise.pk,
            text: $scope.send_message
        }
        $http.post(BASE_URL + 'messages/', data).then(function (response) {
            $scope.messages.push(response.data)
            console.log($scope.conversation_choise.messages)
            $scope.send_message = '';
            $scope.messages = []
            $scope.getMessages($scope.conversation_choise.pk, null)
        })
    }

});
