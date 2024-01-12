myMedBookController.controller('bachecaController', function ($scope, $http, $interval, $timeout, $stateParams, Upload) {
    $scope.posts = [];
    $scope.currentPage = 1;
    $scope.URL_IMAGE = URL_IMAGE
    $scope.listPosts = function () {
        $('.mobile_MMB').show()
        $('.mobile_CDV').hide()
        $scope.groups = [];
        $scope.message = "";
        $scope.callRows('GET', 'post/?page=' + $scope.currentPage, "", {}, function (response) {
            $scope.item_idx = [];
            /**prima di salvarmi le post aggiorno lo stato di non letto a letto alle notifiche passandogli un vettore di id */
            $scope.count = response.count;
            angular.forEach(response.results, function (item) {
                $scope.item_idx.push(item.pk)
                $scope.posts.push(item)
            });
            $http.post(BASE_URL + 'devices/checkNotificationAsRead/', { 'item_idx': $scope.item_idx, 'item_type': 'posts' }).then(
                function () {
                    $http.get(BASE_URL + 'devices/notifications/').then(function (response) {
                        $scope.notifications = response.data;
                    });
                }
            )
        });
    }
    /*$interval(function () {
        $scope.listPosts();
    }, 5000);*/
    $scope.incrementPage = function () {
        $scope.currentPage += 1;
        $scope.listPosts();
    }
    /*$interval(function () {
        $scope.listPosts()
    }, 5000);*/


    $scope.init = function () {
        $(".mmb_menu").removeClass('mmb_selected');
        $(".mmb_bacheca").addClass('mmb_selected');
        $scope.listPosts();
    }

    $scope.uploadFiles = function (file, pk, callback) {
        if (!file)
            return;
        Upload.http({
            url: BASE_URL + 'upload/post/?pk=' + pk,
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

    $scope.publicationPost = function (picFile) {
        if ($scope.groups.length <= 0) {
            alert("condividere con uno o più gruppi")
            return;
        }
        $scope.callRows('POST', 'post/', '', { 'text': $scope.message, 'circle': $scope.groups }, function (response) {
            $scope.currentPage = 1;
            $scope.posts = [];
            if ($scope.picFile) {
                $scope.uploadFiles($scope.picFile, response.pk, function () {
                    $scope.picFile = null
                    $scope.listPosts();
                });
            }
            else{
                $scope.listPosts();
            }

        });
    }

    $scope.addComment = function (item, index) {
        var comment = $("#comment_" + index).val()
        if (!comment) {
            alert('Campo commento vuoto');
            return;
        }
        $scope.callRows('POST', 'comment/', '', {
            'text': $("#comment_" + index).val(), 'post': item
        }, function () {
            $("#comment_" + index).val('')
            $scope.currentPage = 1;
            $scope.posts = [];
            $scope.listPosts();
        });
    }
    $scope.removePost = function (item) {
        $scope.callRows('DELETE', 'post/' + item + '/', '', {}, function () {
            $scope.currentPage = 1;
            $scope.posts = [];
            $scope.listPosts();
        });
    };

});