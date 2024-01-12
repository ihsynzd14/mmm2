# DJANGO
```
PROJ_FOLDER=mymedbook
GIT_URL=git@gitlab.netfarm.it:vics/mymedbook/django_mymedbook.git
GIT_FOLDER=django_mymedbook
```

## virtualenv
```
## installare virtualenv
pip install virtualenv

## creare folder per il progetto, conterrà venv e il clone del repository
mkdir $PROJ_FOLDER
cd $PROJ_FOLDER
virtualenv venv
it

## attivazione virtualenv
. venv/bin/activate
```


## clonare e configurare progetto
```
git clone $GIT_URL $GIT_FOLDER
 
## installare dipendenze
cd $GIT_FOLDER
pip install -r requirements.txt
```
git ## configurare per l'esecuzione da vscode
```
mkdir .vscode

# crea configurazione
cat > .vscode/settings.json << EOF
{
   "python.linting.pylintEnabled": false,
   "python.pythonPath": "../venv/bin/python"
}
EOF

# crea launch
cat > .vscode/launch.json << EOF
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Django",
            "type": "python",
            "request": "launch",
            "stopOnEntry": false,
            "pythonPath": "\${config.python.pythonPath}",
            "program": "\${workspaceRoot}/manage.py",
            "cwd": "\${workspaceRoot}",
            "args": [
                "runserver",
                "--noreload",
                "0.0.0.0:8000"
            ],
            "env": null,
            "envFile": "\${workspaceRoot}/.env",
            "debugOptions": [
                "WaitOnAbnormalExit",
                "WaitOnNormalExit",
                "RedirectOutput",
                "DjangoDebugging"
            ]
        }
    ]
}
EOF
```


## INSTALLARE Postgresql e Postgis (se non ancora installati) 
### OSX
```
# install postgresql
brew install postgresql

# install postgis
brew install postgis

## avvio postgresql
brew services start postgresql
```


## Configurare db
```
createuser mymedbook
createdb -O mymedbook mymedbook
psql template1
    alter user mymedbook with password 'mymedbook';
    <<ctrl+d>>

psql mymedbook
   create extension postgis;
   create extension unaccent;
   <<ctrl+d>>
```

## Setup iniziale
```
./manage.py migrate
./manage.py createsuperuser
```

## avviare il server
```
./manage.py runserver
```

## configurare application
da web accedere al pannello di admin ( http://localhost:8000/admin/ )
* applications
* aggiungi applications

