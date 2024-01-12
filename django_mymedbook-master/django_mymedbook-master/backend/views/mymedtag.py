from django.db import transaction

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.compat import is_authenticated
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound

from backend.serializers import *
from backend.models import *
from backend.utils import handle_upload
from backend.views.COCView import serialControl

import json
import urllib
import logging

log = logging.getLogger("django.request")


class IsAuthenticated1(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        return request.user and is_authenticated(request.user)


class MyMedTagView(APIView):
    #permission_classes = (IsAuthenticated1, )

    def get(self, request):
        mymedtag_code = request.query_params.get('code', None)

        # utente non autenticato puo vedere il codice solo se e' segnato come
        # pubblico
        if request.user.is_anonymous():
            application = None
            # puo' vedere solo un utente di MMB con profilo pubblico
            # se non viene passato un codice, essendo lui anonimo, tornare
            # errore
            if mymedtag_code is None:
                raise PermissionDenied()
            # viene passato codice, devo controllare che:
            # - esista un affiliazione attiva con il codice attivo, facente parte di MMB
            mymedtag_code = mymedtag_code.upper()
            try:
                affiliation = StructureAffiliation.objects.get(
                    mymedtag__code=mymedtag_code,  mymedtag__active=True, left__isnull=True, user__public_lifesaver=True)
            except StructureAffiliation.DoesNotExist:
                raise PermissionDenied()

            target_user = affiliation.user
            result = {
                'user': UserProfileMymedbookSerializer(instance=target_user).data,
                'lifesaver': {},
                'attributes_groups': {}
            }
            # compilo i campi con le informazioni del mymedtag
            queryset = AttributeValue.objects.filter(
                user=target_user, lifesaver=True)

            if target_user.lifesaver:
                instance = AttributeValue.objects.get(
                    pk=target_user.lifesaver.pk)
                result['lifesaver'] = AttributeValueSerializer(
                    instance=instance).data
                queryset = queryset.exclude(pk=instance.pk)

            result['attributes_groups'] = AttributeValueSerializer(
                queryset, many=True).data

        # utente autenticato
        else:
            # se viene passato un tag, verifico che esista e sia attivo
            if mymedtag_code is not None:
                try:
                    mymedtag_instance = MyMedTag.objects.get(
                        code=mymedtag_code, active=True)
                except MyMedTag.DoesNotExist:
                    raise NotFound('User Not found')

            # se non viene passato un codice ritorno le informazioni relative
            # al profilo autenticato
            if mymedtag_code is None:
                target_user = request.user

            application = request.auth.application.client_id

            # l'application e' it.netfarm.mymedbook.mymedtag:
            if application == 'it.netfarm.mymedbook.mymedtag':
                if mymedtag_code is not None:
                    mymedtag_code = mymedtag_code.upper()
                    # se il tag passato e' relativo all'utente autenticato come
                    # AFFILIATO ritorno le informazioni relative al proprio
                    # profilo
                    try:
                        affiliation = StructureAffiliation.objects.get(
                            user=request.user.id, mymedtag__code=mymedtag_code,  mymedtag__active=True, left__isnull=True)
                    except StructureAffiliation.DoesNotExist:
                        # se il tag passato e' relativo all'utente autenticato
                        # come MEMBRO ritorno le informazioni relative al
                        # proprio profilo
                        try:
                            affiliation = StructureMembership.objects.get(
                                user=request.user.id, mymedtag__code=mymedtag_code,  mymedtag__active=True, left__isnull=True)
                        except StructureMembership.DoesNotExist:
                            # se il tag passato e' pubblico, ritorno le
                            # informazioni relative al profilo corrispondente
                            try:
                                affiliation = StructureAffiliation.objects.get(
                                    mymedtag__code=mymedtag_code,  mymedtag__active=True, left__isnull=True, user__public_lifesaver=True)
                            except StructureAffiliation.DoesNotExist:
                                raise PermissionDenied()

                    target_user = affiliation.user

            # l'application e' it.netfarm.mymedbook.cdv o
            # it.netfarm.mymedbook.web :
            elif application == 'it.netfarm.mymedbook.cdv' or application == 'it.netfarm.mymedbook.web':
                if mymedtag_code is not None:
                    # se il tag passato e' relativo all'utente autenticato come
                    # AFFILIATO ritorno le informazioni relative al proprio
                    # profilo
                    try:
                        affiliation = StructureAffiliation.objects.get(
                            user=request.user.id, mymedtag__code=mymedtag_code,  mymedtag__active=True, left__isnull=True)
                    except StructureAffiliation.DoesNotExist:
                        # se il tag passato e' relativo all'utente autenticato
                        # come MEMBRO ritorno le informazioni relative al
                        # proprio profilo
                        try:
                            affiliation = StructureMembership.objects.get(
                                user=request.user.id, mymedtag__code=mymedtag_code,  mymedtag__active=True, left__isnull=True)
                        except StructureMembership.DoesNotExist:
                            # controllo che il codice faccia parte di un
                            # profilo pubblico
                            try:
                                affiliation = StructureAffiliation.objects.get(
                                    mymedtag__code=mymedtag_code,  mymedtag__active=True, left__isnull=True, user__public_lifesaver=True)
                            except StructureAffiliation.DoesNotExist:
                                # controllo che l'utente autenticato sia un
                                # dipendente della struttura CDV
                                member = request.user.structuremembership_set.filter(
                                    structure=2)
                                if len(member) > 0:
                                    # controllo che il codice appartenga ad un
                                    # utente affiliato con la struttura
                                    try:
                                        affiliation = StructureAffiliation.objects.get(
                                            mymedtag__code=mymedtag_code,  mymedtag__active=True, left__isnull=True, structure=2)
                                    except StructureAffiliation.DoesNotExist:
                                        raise PermissionDenied()
                                    # se il codice appartiene ad un ospite mi
                                    # salvo l'istanza
                                    target_user = affiliation.user
                                else:
                                    # non sei un membro della struttura e il
                                    # profilo richiesto e' privato
                                    raise PermissionDenied()
                            else:
                                # e' un profilo pubblico
                                target_user = affiliation.user
                        else:
                            target_user = affiliation.user
                    else:
                        target_user = request.user

            else:
                raise ValidationError('Invalid application')
            # TODO:
            # l'utente di cui si chiede il profilo ha condiviso il profilo un
            # gruppo di cui fa parte
            result = {
                'user': UserProfileMymedbookSerializer(instance=target_user).data,
                'lifesaver': {},
                'attributes_groups': {}
            }

            queryset = AttributeValue.objects.filter(
                user=target_user, lifesaver=True)

            if target_user.lifesaver:
                instance = AttributeValue.objects.get(
                    pk=target_user.lifesaver.pk)
                result['lifesaver'] = AttributeValueSerializer(
                    instance=instance).data
                queryset = queryset.exclude(pk=instance.pk)

            result['attributes_groups'] = AttributeValueSerializer(
                queryset, many=True).data

        if application is not None and application == 'it.netfarm.mymedbook.cdv':
            therapies = Therapy.objects.filter(
                user=target_user, active=True).order_by('-modified')
        else:
            therapies = Therapy.objects.filter(
                user=target_user, active=True, lifesaver=True).order_by('-modified')

        if len(therapies) > 0:
            result['therapies'] = []
            for therapy in therapies:
                therapy_set = {
                    'pk': therapy.pk,
                    'file': '',
                    'info': '',
                    'modified': therapy.modified
                }
                documents = therapy.attachments.all()
                # la terapia dei documenti associati prendo l'ultimo
                # perche' quello valido
                if len(documents) > 0:
                    document = documents.order_by('created').last()
                    if(document.document):
                        therapy_set['file'] = str(document.document)
                # se non ha documenti salvo solo il nome della terapia
                else:
                    therapy_set['info'] = therapy.drug
                result['therapies'].append(therapy_set)

        ### INTEGRAZIONE INFORMAZIONI COC ###
        affiliationCOC = StructureAffiliation.objects.filter(
            user=target_user, structure__code_type='fast_help')
        if affiliationCOC.count() > 0:
            # per ogni struttura di tipo fast_help a cui e' affiliato l'utente
            # salvo le azioni che ha salvato come coppia (code, value)
            result['fast_help'] = {}
            for affiliation in affiliationCOC:
                serials = SerialCOC.objects.filter(affiliation=affiliation)
                serials_valid = []
                for serial in serials:
                    if serialControl(serial.pk):
                        serials_valid.append(serial)
                    if len(serials_valid) > 0:
                        actionsResult = []
                        for structureCOC in Structure.objects.filter(structureaffiliation=affiliation, code_type='fast_help').all():
                            actionsResult.append({'call_coc': structureCOC.phone_number})
                            if structureCOC.mobile_number:
                                actionsResult.append({'sms': structureCOC.mobile_number})
                            actionsResult.append({'pk': structureCOC.pk})
                            for action in affiliation.actioncoc_set.all():
                                actionsResult.append({action.action_type: action.value})
                            result['fast_help'].update({structureCOC.name: actionsResult})
            if len(result['fast_help'])<=0:
                del result['fast_help']
        else:
            result['fast_help'] = None

        return Response(result)
