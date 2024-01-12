from django.db import transaction

from django.contrib.gis.geos import Point

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound

from backend.serializers import *
from backend.models import *
from backend.utils import handle_upload,handle_upload_document, download_remote_file, MEDIA_AVATAR, MEDIA_TERAPIE, MEDIA_EVENTI

from datetime import datetime,timedelta
import urllib

import re
import base64

import logging
log = logging.getLogger("django.request")

regex = r"maps\.google\.com\/maps\?q=[N|S](\d+\.\d+),[E|W](\d+\.\d+)"

class gestioneSOSTAGSMS(APIView):
    #permission_classes = (IsAuthenticated, )
    #parser_classes = (FileUploadParser, MultiPartParser)

    def post(self, request):
        #Prendo il corpo del post
        data=request.data.copy()
        log.info("SOSTAG REQUEST ARRIVED : %s" % data)
        """ BODY DEL POST
        {
            "mittente": <una stringa contenente il mittente dell'SMS descritto sopra>,
            "messaggio": <una stringa contenente il messaggio dell'SMS descritto sopra>
            "lat": <latitudine>
            "long": <longitudine>
        }

        ESEMPIO:

            {
                "mittente": "KzM5MzMzNDMwOTAwNg",
                "messaggio": "U09TIEFsYXJt",
                "lat": "TjQzLjg5NjM3NQ",
                "long": "RTEwLjU1OTU2MA"
            }

            --- DIVENTA ---

            {
                "mittente": "+393334309006",
                "messaggio": "SOS Alarm",
                "lat": "N43.896375",
                "long": "E10.559560"
            }

        """
        #inizio il decode dei vari campi togliendo il BOM UTF8
        try:
            mittente = base64.decodestring(data.get('mittente',base64.encodestring('EMPTY_TAG'))).replace('\xef\xbb\xbf','')
        except:
            log.error('SOSTAG SENDER DECODE ERROR : %s' % (repr(data.get('mittente','EMPTY_TAG'))))
            raise PermissionDenied()
        try:
            messaggio = base64.decodestring(data.get('messaggio',base64.encodestring('EMTPY_MSG'))).replace('\n',' ').replace('\r',' ').replace('\xef\xbb\xbf','')
        except:
            log.error('SOSTAG MESSAGE DECODE ERROR : %s' % (repr(data.get('messaggio','EMTPY_MSG'))))
            raise PermissionDenied()
        try:
            lat = base64.decodestring(data.get('lat',base64.encodestring('EMPTY_LAT'))).replace(',','.').replace('\xef\xbb\xbf','')
        except:
            log.error('SOSTAG LATITUDE DECODE ERROR : %s' % (repr(data.get('lat','EMTPY_LAT'))))
            raise PermissionDenied()
        try:
            lon = base64.decodestring(data.get('long',base64.encodestring('EMPTY_LON'))).replace(',','.').replace('\xef\xbb\xbf','')
        except:
            log.error('SOSTAG LONGITUDE DECODE ERROR : %s' % (repr(data.get('long','EMTPY_LON'))))
            raise PermissionDenied()

        try:
            log.info("SOSTAG MITTENTE: '%s' (type:%s) MESSAGGIO:'%s'(type:%s)" % (mittente,type(mittente),messaggio,type(messaggio)))
            #Cerco un'affiliazione attiva che abbia il codice ricevuto
            affiliation = StructureAffiliation.objects.get(
                mymedtag__code=mittente,  
                mymedtag__active=True)
            if affiliation:
                if affiliation.structure:
                    #controllo che l'affiliazione sia per una struttura con sostag abilitato
                    if affiliation.structure.sostag_enabled:
                        log.info("SOSTAG AFFILIATION FOUND")
                        #cerco un'eventuale richiesta di assistenza non gestita, per la stessa affiliazione, che sia stata ricevuta nelle ultime 24 ore
                        existingAssistanceRequest = AssistanceRequest.objects.filter(
                            affiliation=affiliation,
                            handled=False,
                            date__gte=(datetime.now() - timedelta(days=1)))
                        if (existingAssistanceRequest.count()==0):
                            log.info("SOSTAG existingAssistanceRequest.count()==0")
                            coordinates=None
                            #ricavo le coordinate dal messaggio ricevuto
                            if lat and lat!='EMPTY_LAT' and lon and lon!='EMTPY_LON':
                                log.info("SOSTAG COORD = %s,%s" % (repr(lat),repr(lon)))
                                try:
                                    if lat[0]=='N':
                                        lat=float(lat[1:])
                                    else:
                                        lat=-float(lat[1:])
                                    if lon[0]=='E':
                                        lon=float(lon[1:])
                                    else:
                                        lon=-float(lon[1:])
                                    log.info("SOSTAG PARSED COORD = %s,%s" % (lat,lon))
                                    coordinates=Point(lat,lon)
                                except Exception as e:
                                    log.info("SOSTAG COORD PARSE ERROR")
                            else:
                                log.info("SOSTAG COORD NOT FOUND")
                            #print messaggio,coordinates
                            #creo la richiesta di assistenza
                            AssistanceRequest.objects.create(
                                affiliation=affiliation,
                                latlng=coordinates,
                                date=datetime.now(),
                                structure=affiliation.structure)
                            log.info("SOSTAG RICHIESTA ASSISTENZA CREATA")
                        #else: non creo nulla perche' esiste gia' una richiesta (FASE2 bisogna mettere in coda alla richiesta i dettagli ricevuti
                    else:
                        log.error("SOSTAG AFFILIATION FOUND BUT WITH WRONG STRUCTURE %s - %s " % (affiliation.structure,affiliation.structure.sostag_enabled))
                        raise PermissionDenied()                    
                else:
                    log.error("SOSTAG AFFILIATION FOUND BUT WITHOUT STRUCTURE")
                    raise PermissionDenied()
            else:
                log.error("SOSTAG AFFILIATION NOT FOUND")
                raise PermissionDenied()    
        except StructureAffiliation.DoesNotExist:
            log.error("SOSTAG StructureAffiliation.DoesNotExist")
            raise PermissionDenied()
        return Response({'result':'OK'})
