var myMedBookController = angular.module('myMedBookController', []);

var listLabelGroups = {
    'operatore_sanitario_cdv': {
        'text': 'Operatore Sanitario',
        'tag': 'operatori_sanitari_CDV'
    },
    'animatore_cdv': {
        'text': 'Animatore',
        'tag': 'animatore_CDV'
    },
    'URP_cdv': {
        'text': 'URP',
        'tag': 'URP_CDV',
    },
    'direttore_cdv': {
        'text': 'Direttore',
        'tag': 'direttore_CDV'
    },
    'portiere_cdv': {
        'text': 'Portiere',
        'tag': 'portiere_CDV'
    }
}
var schemaProfile = [
    {
        label: "first_name",
        name: "Nome*",
        datatype: "text",
        require: true,
        editable: true
    }, {
        label: "last_name",
        name: "Cognome*",
        datatype: "text",
        require: true,
        editable: true
    }, {
        label: "email",
        name: "Email*",
        datatype: "text",
        require: true,
        editable: true
    }, {
        label: "birthday",
        name: "Data di nascita",
        datatype: "date",
        editable: true
    }, {
        label: "sex",
        name: "Sesso",
        datatype: "select",
        editable: true,
        option: []
    }, {
        label: "town",
        name: "Domicilio",
        datatype: "text",
        editable: true
    }, {
        label: "height",
        name: "Altezza (cm)",
        datatype: "text",
        editable: true
    }, {
        label: "weight",
        name: "Peso (Kg)",
        datatype: "text",
        editable: true
    }, {
        label: "bmi",
        name: "BMI",
        datatype: "text",
        editable: false
    }, {
        label: "phone",
        name: "Telefono",
        datatype: "text",
        editable: true
    }];

var schemaRegistration = [
    {
        label: "first_name",
        name: "Nome*",
        datatype: "text",
        require: true,
    }, {
        label: "last_name",
        name: "Cognome*",
        datatype: "text",
        require: true
    }, {
        label: "email",
        name: "Email*",
        datatype: "text",
        require: true
    }, {
        label: "birthday",
        name: "Data di nascita",
        datatype: "date",
    }, {
        label: "sex",
        name: "Sesso",
        datatype: "select",
        options: []
    }, {
        label: "town",
        name: "Città",
        datatype: "text",
    }, {
        label: "height",
        name: "Altezza (cm)",
        datatype: "text",
    }, {
        label: "weight",
        name: "Peso (Kg)",
        datatype: "text",
    }, {
        label: "phone",
        name: "Telefono",
        datatype: "text",
        editable: true
    }, {
        label: "password",
        name: "Password*",
        datatype: "password",
        require: true
    }, {
        label: "password_check",
        name: "Ripeti Password*",
        datatype: "password",
        require: true
    }]

var files_schema = [{
    label: "files_field",
    title: " un file al tuo dossier",
    object: "files",
    items: [
        /*{
            label: "document",
            title: "Nome",
            type: "text",
            required: true
        }, {
            label: "desc",
            title: "Descrizione",
            type: "text",
            required: true
        }, {
            label: "meta_info",
            title: "Altro",
            type: "text",
            required: true
        }, */{
            label: "files_field",
            title: "File",
            type: "file",
            required: true
        }
    ]
}];
var dossier_schema = [{
    label: "dossier_field",
    title: " un nuovo dossier medico",
    object: "dossier",
    items: [
        {
            label: "name",
            title: "Nome",
            type: "text",
            required: true
        }, {
            label: "meta_info",
            title: "Note",
            type: "text",
            required: false
        }, {
            label: "fiscal_code",
            title: "Codice fiscale",
            type: "text",
            required: false
        }, {
            label: "circle",
            title: "Gruppi",
            type: "multiselect",
            nameTable: "circle",
            options: [],
            required: true
        }
    ]
}];
var dossier_schema_detail = [{
    label: "dossier_field",
    title: " un nuovo dossier medico",
    object: "dossier",
    items: [
        {
            label: "name",
            title: "Nome",
            type: "text",
            required: true
        }, {
            label: "meta_info",
            title: "Note",
            type: "text",
            required: false
        }, {
            label: "fiscal_code",
            title: "Codice fiscale",
            type: "text",
            required: false
        }, {
            label: "circle",
            title: "Gruppi",
            type: "multiselect",
            nameTable: "circle",
            options: [],
            required: false
        }, {
            label: "document_set",
            title: "Documenti",
            type: "file",
            nameTable: "document_set",
            required: false
        }, {
            label: "event_set",
            title: "Eventi",
            type: 'custom_for_dossier',
            required: false
        }, {
            label: "therapy_set",
            title: "Terapie",
            type: 'custom_for_dossier',
            required: false
        }
    ]
}];

var gruppo_schema = [{
    label: "gruppo_field",
    title: " un nuovo gruppo",
    object: "circle",
    items: [
        {
            label: "name",
            title: "Nome",
            type: "text",
            required: true
        }, {
            label: "circleaffiliation_set",
            title: "Utenti gruppo",
            type: "multiple_input",
            items: [
                {
                    label: "email",
                    title: "Email",
                    type: "email",
                    required: true
                }
            ]
        }
    ]
}];

var agenda_schema = [{
    label: "agenda_field",
    title: " una nuova voce nell'agenda",
    object: "event",
    items: [
        {
            label: "name",
            title: "Name",
            type: "text",
            required: true
        }, {
            label: "desc",
            title: "Descrizione",
            type: "textarea",
            required: false
        }, {
            label: "start_date",
            title: "Data Inizio",
            type: "dateI",
            required: true
        }, {
            label: "start_hour",
            title: "Orario Inizio",
            type: "time",
            required: true
        }, {
            label: "end_date",
            title: "Data Fine",
            type: "dateF",
            required: true
        }, {
            label: "end_hour",
            title: "Orario Fine",
            type: "time",
            required: true
        }, {
            label: "event_type",
            title: "Tipo di evento",
            type: "select",
            required: true,
            options: []
        }, {
            label: "circle",
            title: "Gruppi",
            type: "multiselect",
            nameTable: "circle",
            options: [],
            required: false
        }, {
            label: "dossier",
            title: "Dossier",
            type: "select",
            nameTable: "dossier",
            options: [],
            required: false
        }, {
            label: "notification",
            title: "Notifica",
            type: "checkbox",
            default: false,
            required: false
        }, {
            label: "authority",
            title: "Ente",
            type: "text",
            required: false
        }, {
            label: "address",
            title: "Indirizzo",
            type: "text",
            required: false
        },{
            label: "attachments",
            title: "File",
            type: "file",
            required: false
        },

    ]
}];

var terapia_schema = [
    {
        label: "terapia_schema",
        title: " una nuova terapia",
        object: "therapy",
        items: [
            {
                label: "name",
                title: "Nome",
                type: "text",
                required: true
            }, {
                label: "drug",
                title: "Farmaco",
                type: "text",
                required: true
            }, {
                label: "treatment_plan",
                title: "Piano trattamento",
                type: "text",
                required: true
            }, {
                label: "instructions",
                title: "Avvertenze",
                type: "text",
                required: false
            }, {
                label: "start_date",
                title: "Data di inizio",
                type: "dateI",
                required: true
            }, {
                label: "end_date",
                title: "Data di termine",
                type: "dateF",
                required: true
            }, {
                label: "posologiestherapy_set",
                title: "Orario terapia",
                type: "multiple_input",
                items: [
                    {
                        label: "hour",
                        title: "Orario",
                        type: "time",
                        required: false
                    },
                    {
                        label: 'posology',
                        title: 'Posologia',
                        type: 'text',
                        required: false
                    }
                ]
            }, /*{
                label: "therapy_type",
                title: "Tipologia",
                type: "select",
                nameTable: "TherapyTypes",
                options: [],
                required: false
            },*/ {
                label: "active",
                title: "Attiva",
                type: "checkbox",
                default: true,
                required: false
            }, {
                label: "notification",
                title: "Notifica",
                type: "checkbox",
                default: false,
                required: false
            }, {
                label: "lifesaver",
                title: "Salvavita",
                type: "checkbox",
                default: false,
                required: false
            }, /*{
                label: "users",
                title: "Utenti gruppo",
                type: "multiple_input",
                items: [
                    {
                        label: "email",
                        title: "Email",
                        type: "email",
                        required: false
                    }
                ]
            },*/ {
                label: "attachments",
                title: "File",
                type: "file",
                required: false
            }]
    }];

function checkPage() {
    var path_tmp = window.location.href;
    if (path_tmp.indexOf('mymedtag') < 0 && window.location.hash == '' && document.referrer == '') {
        window.location = '#/';
        console.log('SALTO');
    }
}

checkPage();
