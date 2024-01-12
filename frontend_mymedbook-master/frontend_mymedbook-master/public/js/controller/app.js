'use strict';
/*sono i moduli rispettivi di ogni libreria, nel caso di ngRoute serve ad esempio per utilizzare il $routeProvider*/
var app = angular.module('myMedBookApp', [
	'angular-oauth2',
	'ui.router',
	'ngResource',
	'ngAnimate',
	'myMedBookController',
	'ngMaterial',
	'ui.calendar',
	'ui.bootstrap',
	//'ui.bootstrap.datetimepicker',
	'720kb.datepicker',
	'ngCookies',
	'mgcrea.ngStrap',
	'ngFileUpload',
	'ngInputModified',
	'ngLodash',
	'autocomplete',
]);
function isSecure() {
	return (window.location.protocol === 'https:');
}
app.config(['$stateProvider', '$sceDelegateProvider', '$httpProvider', '$mdDateLocaleProvider', 'OAuthProvider', 'OAuthTokenProvider', '$provide', '$resourceProvider',
	function ($stateProvider, $sceDelegateProvider, $httpProvider, $mdDateLocaleProvider, OAuthProvider, OAuthTokenProvider, $provide, $resourceProvider) {
		$stateProvider.
			state('login', {
				url: "/",
				views: {
					"main-container": {
						templateUrl: 'login.html',
						controller: 'loginController',
					}
				}
			}).state('main', {
				url: "/",
				views: {
					"main-container": {
						templateUrl: 'templates/menu.html',
						controller: 'menuController'
					},
					"view-content": {
						templateUrl: 'templates/profilo.html',
						controller: 'profiloController'
					},
				}
			}).state('main.bacheca', {
				url: "bacheca",
				views: {
					"view-content": {
						templateUrl: 'templates/bacheca.html',
						controller: 'bachecaController'
					},
				}
			}).state('main.dossier', {
				url: "dossier",
				views: {
					"view-content": {
						templateUrl: 'templates/dossier.html',
						controller: 'dossierController'
					},
				}
			}).state('main.agenda', {
				url: "agenda",
				views: {
					"view-content": {
						templateUrl: 'templates/agenda.html',
						controller: 'agendaController'
					},
				}
			}).state('main.gruppi', {
				url: "gruppi",
				views: {
					"view-content": {
						templateUrl: 'templates/gruppi.html',
						controller: 'gruppiController'
					},
				}
			}).state('main.terapia', {
				url: "terapia",
				views: {
					"view-content": {
						templateUrl: 'templates/terapia.html',
						controller: 'terapiaController'
					},
				}
			}).state('main.profilo', {
				url: "profilo",
				views: {
					"view-content": {
						templateUrl: 'templates/profilo.html',
						controller: 'profiloController'
					},
				}
			}).state('main.mymedtag', {
				url: "mymedtag",
				views: {
					"view-content": {
						templateUrl: 'templates/mymedtag.html',
						controller: 'mymedtagController'
					},
				}
			}).state('main.privacy', {
				url: "privacy",
				views: {
					"view-content": {
						templateUrl: 'templates/privacy.html',
						controller: 'privacyController'
					},
				}
			}).state('main.ingressi', {
				url: "ingressi",
				views: {
					"view-content": {
						templateUrl: 'templates/ingressi.html',
						controller: 'ingressiController'
					},
				}
			}).state('main.alarm', {
				url: "allarmi",
				views: {
					"view-content": {
						templateUrl: 'templates/gestioneAllarmi.html',
						controller: 'gestioneAllarmiController'
					},
				}
			}).state('main.ospiti', {
				url: "ospiti",
				views: {
					"view-content": {
						templateUrl: 'templates/gestioneOspiti.html',
						controller: 'gestioneOspitiController'
					},
				}
			}).state('main.dipendenti', {
				url: "dipendenti",
				views: {
					"view-content": {
						templateUrl: 'templates/gestioneDipendenti.html',
						controller: 'gestioneDipendentiController'
					},
				}
			}).state('main.admin', {
				url: "admin",
				views: {
					"view-content": {
						templateUrl: 'templates/admin.html',
						controller: 'adminController'
					},
				}
			}).state('main.change_password', {
				url: "change_password",
				views: {
					"view-content": {
						templateUrl: 'templates/change_password.html',
						controller: 'changePasswordController'
					},
				}
			}).state('main.chat', {
				url: "chat",
				views: {
					"view-content": {
						templateUrl: 'templates/chat.html',
						controller: 'chatController'
					},
				}
			}).state('main.gestioneRichiesteCOC', {
				url: "gestioneRichiesteCOC",
				views: {
					"view-content": {
						templateUrl: 'teleassistenza/gestioneRichiesteCOC.html',
						controller: 'gestioneRichiesteCOCController'
					},
				}
			}).state('main.gestioneAffiliatiCOC', {
				url: "gestioneAffiliatiCOC",
				views: {
					"view-content": {
						templateUrl: 'teleassistenza/gestioneAffiliatiCOC.html',
						controller: 'gestioneAffiliatiCOCController'
					},
				}
			}).state('main.gestioneMembriCOC', {
				url: "gestioneMembriCOC",
				views: {
					"view-content": {
						templateUrl: 'teleassistenza/gestioneMembriCOC.html',
						controller: 'gestioneMembriCOCController'
					},
				}
			}).state('main.serialsCOC', {
				url: "serialsCOC",
				views: {
					"view-content": {
						templateUrl: 'teleassistenza/serialsCOC.html',
						controller: 'serialsCOCController'
					},
				}
			});
		$provide.decorator('$q', function ($delegate) {
			function seqAll(promises) {
				var d = $delegate.defer();
				var results = [];
				var i = 0;

				recurse(promises[i]);

				function recurse(promise) {
					i++;
					promise.then(function (data) {
						results.push(data);
						if (i < promises.length)
							recurse(promises[i]);
						else
							d.resolve(results);
					}).catch(function (error) {
						d.reject('promises[' + (i - 1) + ']' + ' rejected with error: ' + error);
					});
				}
				return d.promise;
			}
			$delegate.seqAll = seqAll;
			return $delegate;
		});
		//OAuth
		OAuthProvider.configure({
			baseUrl: URL_AUTH,
			clientId: CLIENT_ID,
			grantPath: '/oauth/token/',
			revokePath: '/oauth/revoke_token/'
		});
		OAuthTokenProvider.configure({
			name: 'token',
			options: {
				secure: isSecure()
			}
		});
		//CONFIGURAZIONE DATE
		// Example of a French localization.
		$mdDateLocaleProvider.months = ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre'];
		$mdDateLocaleProvider.shortMonths = ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Sett', 'Ott', 'Nov', 'Dic'];
		$mdDateLocaleProvider.days = ['Domenica', 'Lunedi', 'Martedi', 'Mercoledi', 'Giovedi', 'Venerdi', 'Sabato'];
		$mdDateLocaleProvider.shortDays = ['Dom', 'Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab'];
		// Can change week display to start on Monday.
		$mdDateLocaleProvider.firstDayOfWeek = 1;

		// Example uses moment.js to parse and format dates.
		$mdDateLocaleProvider.parseDate = function (dateString) {
			var m = moment(dateString, 'l', true);
			return m.isValid() ? m.toDate() : new Date(NaN);
		};

		$mdDateLocaleProvider.formatDate = function (date) {
			return moment(date).format('DD/MM/YYYY HH:mm');
		};
		// In addition to date display, date components also need localized messages
		// for aria-labels for screen-reader users.
		$mdDateLocaleProvider.weekNumberFormatter = function (weekNumber) {
			return 'Settimana ' + weekNumber;
		};

		$mdDateLocaleProvider.msgCalendar = 'Calendario';
		$mdDateLocaleProvider.msgOpenCalendar = 'Apri il calendario';

//		$httpProvider.defaults.xsrfCookieName = 'csrftoken';
//		$httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
//		$httpProvider.defaults.withCredentials = true;
		/*$sceDelegateProvider.resourceUrlWhitelist([
			'http://artemisia.netfarm.it:8000/**'
		]);*/

	}
]).directive("hideToolbar", function () {
	return {
		restrict: 'AEC',
		link: function (scope, elem, attr) {
			$(".fc-toolbar").hide();
		}
	}
}).directive('timepickerDir', function ($rootScope, $http, $q) {
	return {
		restrict: 'AEC',
		link: function (scope, element, attr) {
			var options = {
				now: "12:35", //hh:mm 24 hour format only, defaults to current time
				twentyFour: true, //Display 24 hour format, defaults to false
				upArrow: 'wickedpicker__controls__control-up', //The up arrow class selector to use, for custom CSS
				downArrow: 'wickedpicker__controls__control-down', //The down arrow class selector to use, for custom CSS
				close: 'wickedpicker__close', //The close class selector to use, for custom CSS
				hoverState: 'hover-state', //The hover state class to use, for custom CSS
				title: 'Timepicker', //The Wickedpicker's title,
				showSeconds: false, //Whether or not to show seconds,
				secondsInterval: 1, //Change interval for seconds, defaults to 1
				minutesInterval: 1, //Change interval for minutes, defaults to 1
				beforeShow: null, //A function to be called before the Wickedpicker is shown
				show: null, //A function to be called when the Wickedpicker is shown
				clearable: false, //Make the picker's input clearable (has clickable "x")
			};
			$('.timepicker').wickedpicker(options);
		},
	}
}).run(['$rootScope', '$window', 'OAuth', function ($rootScope, $window, OAuth) {
	$rootScope.$on('oauth:error', function (event, rejection) {
		// Ignore `invalid_grant` error - should be catched on `LoginController`.
		if ('invalid_grant' === rejection.data.error) {
			return $window.location.href = '#/';
		}

		// Refresh token when a `invalid_token` error occurs.
		if ('invalid_token' === rejection.data.error) {
			return OAuth.getRefreshToken();
		}

		// Redirect to `/login` with the `error_reason`.
		return $window.location.href = '#/';
	});

}]).value('structure', null)
.constant('uiDatetimePickerConfig', {
	dateFormat: 'dd/MM/yyyy',
	html5Types: {
		'date': 'yyyy-MM-dd',
		'month': 'yyyy-MM'
	},
	initialPicker: 'date',
	reOpenDefault: false,
	enableDate: true,
	enableTime: false,
	buttonBar: {
		show: true,
		now: {
			show: true,
			text: 'Now',
			cls: 'btn-sm btn-default'
		},
		today: {
			show: true,
			text: 'Today',
			cls: 'btn-sm btn-default'
		},
		clear: {
			show: true,
			text: 'Clear',
			cls: 'btn-sm btn-default'
		},
		date: {
			show: true,
			text: 'Date',
			cls: 'btn-sm btn-default'
		},
		close: {
			show: true,
			text: 'Close',
			cls: 'btn-sm btn-default'
		}
	},
	closeOnDateSelection: true,
	closeOnTimeNow: true,
	appendToBody: false,
	altInputFormats: [],
	ngModelOptions: {},
	saveAs: false,
	readAs: false
})
.directive('castToInteger', function () {
    return {
        restrict: 'A',
        require: 'ngModel',
        link: function(scope, element, attrs, ngModel) {
            ngModel.$parsers.unshift(function(value) {
				console.log(value)
                return parseInt(value, 10);
            });
        }
    };
});

//Tutte le richieste verranno fatte prima di qualsiasi altra chiamata
/*angular.element(document).ready(function () {
});*/