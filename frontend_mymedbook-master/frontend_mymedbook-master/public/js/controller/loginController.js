myMedBookController.controller('loginController', function ($scope, $http, $stateParams, $cookies, $rootScope, OAuth, $q, $timeout) {
    $cookies.remove("profilo");
    $cookies.remove("token");
    $cookies.remove("admin")
    $("#header .user").hide();
    $(".mobile").hide();
    function refreshToken(OAuth) {
        OAuth.getRefreshToken().then(function (response) {
            $timeout(refreshToken, response.data.expires_in / 2 * 1000, true, OAuth);
        });
    }
    $scope.login = function () {
        if (!$scope.email || !$scope.password)
            return;

        (function () {
            if (!OAuth.isAuthenticated())
                return $q.resolve();
            return OAuth.revokeToken();
        })().then(function () {
            OAuth.getAccessToken({ username: $scope.email, password: $scope.password })
                .then(
                function successCallback(success_response) {
                    $http.get(BASE_URL + "profile/").then(function successCallback(response) {
                        if(!response.data.active){
                            $("#modal_user_not_active").modal("show");
                            return;
                        }
                        $scope.profile = response.data;
                        if (response.data.is_staff===true){
                            window.location.href = "#/admin";
                            return;
                        }
                        else{
                            window.location.href = "#/profilo";
                            return;
                        }
                    });
                    //TODO gestione admin che rimanda a lista utenti

                    $timeout(refreshToken, success_response.data.expires_in / 2 * 1000, true, OAuth);
                }, function errorCallback(error_response) {
                    if (error_response.status === 401) {
                        alert("Username o password non valida");
                    }
                    else if (error_response.status === 500) {
                        alert("La lunghezza minima non puo essere meno di 4 caratteri");
                    }
                    else if (error_response.status === 403) {
                        alert("Email o password errate");
                    }
                    else
                        alert("errore di sistema")
                });
        });
    }

    $scope.registrazione = function () {
        if (!$scope.nome || !$scope.cognome || !$scope.email || !$scope.password) {
            alert('Si prega di compilare tutti i campi')
            return;
        }
        if (!$scope.privacy['profilazione'] || !$scope.privacy['posizione'] || !$scope.privacy['trasferimento'] || !$scope.privacy['Informativa']) {
            alert('Prego accettare le condizioni sulla privacy necessarie')
            return;
        }

        var confirm = false;
        if ($scope.password == $scope.password_check)
            confirm = true;

        if (!confirm) {
            alert("Le password non combaciano")
            return;
        }

        var data = {
            email: $scope.email,
            password: $scope.password,
            first_name: $scope.nome,
            last_name: $scope.cognome
        }
        $http({
            method: "POST",
            url: BASE_URL + "register/",
            headers: {
                'Content-Type': "application/json",
            },
            data: data
        }).then(
            function successCallback(success_response_profile) {
                alert('È stata inviata una mail all\'indirizzo indicato per procedere con l\'attivazione');
                $scope.changeView('newregister','login')
            }, function errorCallback(error_response_profile) {
                if(error_response_profile.data.username)
                    alert(error_response_profile.data.username);
                console.log(error_response_profile)
                if (error_response_profile.status === 400) {
                    //la mail che si sta provando a registrare esiste già
                    if (error_response_profile.data.code === "E_VALIDATION")
                        alert("Email già presente");
                }
            });
    }

    $scope.changeView = function (id_hide, id_show) {
        $("#" + id_hide).hide();
        $("#" + id_show).show();
    }

    $scope.openDialogPrivacy = function () {
        $("#modal_privacy").modal("show");
        $("#modal_user_not_active").modal("hide");
    }

    $scope.closeDialogPrivacy = function () {
        $("#modal_privacy").modal("hide");
    }

    $scope.recuperoPassword = function () {
        $(".loginuser").hide();
        $("#recuperapassword").show();
        $("#changePsw").show();
        $("#attivazione_account").hide();
    }
    $scope.invioMailAttivazione = function () {
        $(".loginuser").hide();
        $("#attivazione_account").show();
        $("#modal_user_not_active").modal("hide");
    }
    $scope.closeDialogActivation = function () {
        $("#modal_user_not_active").modal("hide");
    }
    $scope.send_mail_activation_account = function(){
        $http.get(SERVER_URL + 'users/mail/activation/?email='+ $scope.email).then(
            function successCallback(data) {
                alert("email per attivazione invia con successo a " + $scope.email);
                $scope.changeView('attivazione_account', 'login');
            }, function errorCallback(response) {
                alert(response.data.detail);
            });
    }

    $scope.reset = function () {
        $http.post(SERVER_URL + 'users/password/reset/', { email: $scope.email }).then(
            function successCallback(data) {
                alert("email per reset password inviata a " + $scope.email);
                $scope.changeView('recuperapassword', 'login');
            }, function errorCallback(response) {
                alert(response.data.detail);
            });
    }
});
