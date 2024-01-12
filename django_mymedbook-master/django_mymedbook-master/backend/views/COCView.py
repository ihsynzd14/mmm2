from django.db import transaction

from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.template import loader

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.pagination import PageNumberPagination

from backend.serializers import *
from backend.models import *
from backend.utils import handle_upload, download_remote_file, MEDIA_AVATAR, MEDIA_TERAPIE, validate_password

from datetime import datetime, timedelta, date
import urllib
import ast

# La funzione ritorna la lista delle strutture COC di cui l utente
# autenticato e' un affiliato

def serialControl(serial_id):
    # controllo se per questa struttura l'utente ha un seriale valido, se no
    # non lo salvo e passo a quello successivo
    try:
        serial = SerialCOC.objects.get(pk=serial_id)
    except SerialCOC.DoesNotExist:
        pass
    else:
        # se la data di inizio del seriale e' minore  uguale alla data di oggi e la data di termine e' maggiore di oggi
        # allora il seriale e' valido
        end_date_validation = serial.start_date_validation + timedelta(serial.duration*365/12)

        if serial.start_date_validation <= datetime.now().date() and end_date_validation >= datetime.now().date():
            return True

    return False


class COCList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        if request.query_params.get('user_id'):
            try:
                user = UserProfile.objects.get(
                    pk=request.query_params.get('user_id'))
            except UserProfile.DoesNotExist:
                raise ValidationError('User not found')

        if request.query_params.get('structure_id'):
            structures = Structure.objects.filter(code_type='fast_help', structureaffiliation__user=user, pk=request.query_params.get('structure_id'))
        else:
            structures = Structure.objects.filter(code_type='fast_help', structureaffiliation__user=user)

        result = []

        # si cercano tutte le strutture di cui l'utente e' affiliato e che
        # abbiano il codice:fast_help

        for structure in structures:
            try:
                affiliation = StructureAffiliation.objects.get(
                    user=user, structure=structure)
            except StructureAffiliation.DoesNotExist:
                raise ValidationError('Affiliation not found')

            actions = ActionCOC.objects.filter(affiliation=affiliation)
            serials = SerialCOC.objects.filter(
                affiliation=affiliation)
            serials_valid = []
            for serial in serials:
                print serial
                if serialControl(serial.pk):
                    serials_valid.append(serial)
            if len(serials_valid)>0:
                result.append({
                    'structure': StructureSerializer(instance=structure).data,
                    'actions': ActionCOCSerializer(instance=actions, many=True).data,
                    'serials': SerialCOCSerializer(instance=serials, many=True).data
                })
        return Response(result)

class AttributeValuesCOC(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user
        guest_id = request.query_params.get('user_id', None)
        if guest_id is not None:
            try:
                user = UserProfile.objects.get(pk=guest_id)
            except UserProfile.DoesNotExist:
                raise ValidationError('User not found')

        results = []
        # prelevo la struttura dell'utente loggato, se e' sia CDV sia MMB
        # prendo CDV
        structure_user = [1]

        if len(user.structureaffiliation_set.all()) > 0:
            for structure in user.structureaffiliation_set.all():
                 # controllo se per questa struttura l'utente ha un seriale
                 # valido, se no non lo salvo e passo a quello successivo
                serials = SerialCOC.objects.filter(affiliation_id=structure.pk)
                serials_valid = []
                for serial in serials:
                    if serialControl(serial.pk):
                        serials_valid.append(serial)
                if len(serials_valid)>0:
                    structure_user.append(structure.structure_id)

        for group in AttributeGroup.objects.filter(structure__in=structure_user, structure__code_type='fast_help').order_by('sorting'):
            serialized = AttributeGroupSerializer(instance=group).data
            results.append(serialized)
            serialized['attributes'] = []
            group_attribute_values = {}

            # query per prendere tutti gli attribute (non i valori) che
            # andrebbero in quel gruppo
            for attribute in Attribute.objects.filter(group=group).order_by('sorting'):
                serialized_value = {
                    'attribute': AttributeSerializer(instance=attribute).data,
                    'value': None
                }
                if attribute.datatype == 'enum':
                    queryset = Enum.objects.filter(attribute=attribute)
                    serialized_value['enum'] = EnumSerializer(
                        queryset, many=True).data

                serialized['attributes'].append(serialized_value)
                group_attribute_values[attribute.pk] = serialized_value

            # query per prendere tutti gli i valori che andrebbero in quel
            # gruppo
            for attribute_value in AttributeValue.objects.filter(attribute__group=group, user=user):
                attribute = attribute_value.attribute
                serialized_value = AttributeValueSerializer(
                    instance=attribute_value).data
                if attribute.datatype == 'enum':
                    serialized_value['value'] = [attribute_value.enum.pk]
                if group_attribute_values[attribute.pk].get('value', None) == None:
                    # merge tra group_attribute_values[attribute.pk] e serialized_value
                    # TODO: controllare se esista un metodo piu' efficente per
                    # realizzarlo
                    for field in serialized_value:
                        group_attribute_values[attribute.pk][
                            field] = serialized_value[field]
                else:
                    if attribute.datatype == 'enum':
                        group_attribute_values[attribute.pk][
                            'value'] += serialized_value['value']
                    else:
                        group_attribute_values[attribute.pk][
                            'value'] = serialized_value['value']

        return Response(results)
# La funzione restiruisce la lista dei seriali, per la struttura passata
# come parametro, validi per l'utente passato


class ListSerial(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        print request.query_params.get('user_id')
        if request.query_params.get('user_id'):
            try:
                user = UserProfile.objects.get(
                    pk=request.query_params.get('user_id'))
            except UserProfile.DoesNotExist:
                raise ValidationError('User not found')
        if request.query_params.get('structure_id'):
            try:
                structure = Structure.objects.get(
                    pk=request.query_params.get('structure_id'))
            except Structure.DoesNotExist:
                raise ValidationError('Structure not found')
        affiliations = StructureAffiliation.objects.filter(
            user_id=user.pk, structure_id=structure.pk)
        serials = SerialCOC.objects.filter(affiliation_id=affiliations[0].pk)

        return Response(SerialCOCSerializer(instance=serials, many=True).data)


class AllListSerial(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        # if user.groups[0] == 'admin_COC'
        if request.query_params.get('structure_id'):
            try:
                structure = Structure.objects.get(
                    pk=request.query_params.get('structure_id'))
            except Structure.DoesNotExist:
                raise ValidationError('Structure not found')
            serials = SerialCOC.objects.filter(
                structure_id=structure.pk, valid=False)

        return Response(SerialCOCSerializer(instance=serials, many=True).data)

# La funzione salva l'associazione di un utente con il seriale passato, e aggiorna la
# data di inizio validita' del seriale e lilo booleano valid a true


class SaveSerial(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        serial_code = request.data.pop('serial')
        if request.query_params.get('user_id'):
            try:
                user = UserProfile.objects.get(
                    pk=request.query_params.get('user_id'))
            except UserProfile.DoesNotExist:
                raise ValidationError('User not found')
        if request.query_params.get('structure_id'):
            try:
                structure = Structure.objects.get(
                    pk=request.query_params.get('structure_id'))
            except Structure.DoesNotExist:
                raise ValidationError('Structure not found')
        if serial_code:
            try:
                serial = SerialCOC.objects.get(
                    serial=serial_code, structure=structure.pk, valid=False)
            except SerialCOC.DoesNotExist:
                raise ValidationError('Serial not valid')
        affiliations = StructureAffiliation.objects.filter(
            user_id=user.pk, structure=structure.pk)
        serialized = SerialCOCSerializer(instance=serial, data={
                                         'valid': True, 'start_date_validation': request.data.pop('start_date_validation')}, partial=True)
        serialized.is_valid(raise_exception=True)
        serialized.save(affiliation_id=affiliations[0].pk)
        return Response(serialized.data)


# La funzione salva le azioni scelte dall'utente autenticato


class SaveActions(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        data = request.data.copy()
        structure_id = data.get('structure')
        action = data.pop('action')
        # controllare che l'utente sia affiliato a quella struttura
        try:
            structure = Structure.objects.get(
                pk=structure_id)
        except Structure.DoesNotExist:
            raise ValidationError('Structure not found')
        # creo l'azione
        try:
            sa = StructureAffiliation.objects.get(
                structure=structure, user=user)
        except StructureAffiliation.DoesNotExist:
            raise ValidationError('Affiliation not found')

        print action
        if action['action_type'] == 'circle':
            try:
                actionUser = ActionCOC.objects.get(
                    affiliation__in=[sa.pk, ], action_type=action['action_type'], circle_id=action['circle'])
            except ActionCOC.DoesNotExist:
                action['affiliation'] = [sa.pk]
                serialized = ActionCOCSerializer(data=action)
                serialized.is_valid(raise_exception=True)
                serialized.save()
            else:
                actionUser.circle_id = action['circle']
                actionUser.save()
        else:
            try:
                actionUser = ActionCOC.objects.get(
                    affiliation__in=[sa.pk, ], action_type=action['action_type'])
            except ActionCOC.DoesNotExist:
                action['affiliation'] = [sa.pk]
                serialized = ActionCOCSerializer(data=action)
                serialized.is_valid(raise_exception=True)
                serialized.save()
            else:
                actionUser.value = action['value']
                actionUser.save()

        return Response('ok')


class DeleteActions(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request):
        user = request.user
        structure_id = request.query_params.get('structure_id')
        action_type = request.query_params.get('action_type')
        group_id = request.query_params.get('group_id')
        # controllare che l'utente sia affiliato a quella struttura
        try:
            structure = Structure.objects.get(
                pk=structure_id)
        except Structure.DoesNotExist:
            raise ValidationError('Structure not found')
        # creo l'azione
        try:
            sa = StructureAffiliation.objects.get(
                structure=structure_id, user=user)
        except StructureAffiliation.DoesNotExist:
            raise ValidationError('Affiliation not found')

        if action_type == 'circle':
            try:
                actionUser = ActionCOC.objects.get(
                    affiliation__in=[sa.pk, ], action_type=action_type, group_id=group_id)
            except ActionCOC.DoesNotExist:
                pass
            else:
                actionUser.delete()
        else:
            try:
                actionUser = ActionCOC.objects.get(
                    affiliation__in=[sa.pk, ], action_type=action_type)
            except ActionCOC.DoesNotExist:
                raise ValidationError('Action not Found')
            else:
                actionUser.delete()

        return Response('ok')


class AssistanceList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        structure_id = request.query_params.get('structure_id')
        handled = request.query_params.get('handled')
        # controllare che l'utente sia affiliato a quella struttura
        try:
            structure = Structure.objects.get(
                pk=structure_id)
        except Structure.DoesNotExist:
            raise ValidationError('Structure not found')
        try:
            affiliation = StructureMembership.objects.get(
                structure=structure, user=user)
        except StructureMembership.DoesNotExist:
            raise ValidationError('Affiliation not found')
        timestamp = datetime.now() - timedelta(days=1)

        listRequest = AssistanceRequest.objects.filter(structure=structure, date__gte=timestamp).order_by('-created')

        if handled:
            listRequest = listRequest.filter(
                structure=structure, handled=False).order_by('-created')

        return Response(AssistanceRequestSerializer(instance=listRequest, many=True).data)

# La funzione salva una richiesta di assistenza


class SaveAssistanceRequest(APIView):
    #permission_classes = (IsAuthenticated,)
    email_template_name = 'assistanceMailCOC.html'

    def send_mail(self, context, to_email):
        subject = '[MMB] Richiesta di Assistenza'
        body = loader.render_to_string(self.email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, 'noreply@mymedbook.it', [to_email])
        email_message.send()

    def post(self, request):
        data = request.data.copy()
        coord = data.get('latlng', None)
        mymedtag_code = data.pop('code', None) #opzionale
        COC = data.pop('COC')
        return self.doit(request,COC,coord,mymedtag_code)

    def parseCoord(self,coord):
        if coord:
            try:
                coord={'coordinates':ast.literal_eval(coord)}
                
            except:
                return None
        return coord

    def get(self, request):
        data = request.query_params.copy()
        coord = self.parseCoord(data.get('latlng', None))
        mymedtag_code = data.get('code', None) #opzionale
        COC = data.get('COC')
        return self.doit(request,COC,coord,mymedtag_code)
        
    def doit(self,request,COC,coord,mymedtag_code):
        print 'mymedtag: ', mymedtag_code
        if mymedtag_code!=None:
            try:
                mymedtag = MyMedTag.objects.get(code=mymedtag_code, active=True)
            except MyMedTag.DoesNotExist:
                raise ValidationError('Tag not found')
            try:
                user = UserProfile.objects.get(structureaffiliation=mymedtag.structure_affiliation)
            except UserProfile.DoesNotExist:
                raise ValidationError('User not Found')
        else:
            user=request.user

        structures = Structure.objects.filter(pk__in=COC)
        site = ''
        for structure in structures:
            # controllo il MMTCode se valido
            try:
                #affiliation = StructureAffiliation.objects.get(
                #    user=request.user.id, mymedtag__code=mymedtag_code,  mymedtag__active=True, left__isnull=True)
                affiliation_structure = StructureAffiliation.objects.get(
                    user_id=user.pk, structure_id=structure.pk, left__isnull=True)
            except StructureAffiliation.DoesNotExist:
                raise ValidationError('Affiliation not found')

            serials = SerialCOC.objects.filter(affiliation=affiliation_structure)
            serials_valid = []
            for serial in serials:
                if serialControl(serial.pk):
                    serials_valid.append(serial)
                if len(serials_valid) <= 0:
                    return Response({'message': 'ok'})

            # se non esiste gia' una richiesta di assistenza inviata dalla stessa persona non gestita ora allora salvo la richiesta
            # altrimenti non faccio nulla
            lowerbound = datetime.now() - timedelta(hours=1)
            if AssistanceRequest.objects.filter(handled=False, affiliation_id=affiliation_structure.pk, date__gte=lowerbound).count()<=0:
                if coord is not None:
                    site = 'www.google.com/maps/place/%f,%f' % (
                        coord['coordinates'][0], coord['coordinates'][1])
                    coordinates = coord['coordinates']
                    assistance = AssistanceRequest.objects.create(
                        affiliation=affiliation_structure,
                        latlng=Point(coordinates[0], coordinates[1]),
                        date=datetime.now(),
                        structure=structure)
                else:
                    assistance = AssistanceRequest.objects.create(
                        affiliation=affiliation_structure,
                        date=datetime.now(),
                        structure=structure)
                assistance.save()

                actions = ActionCOC.objects.filter(
                    affiliation=affiliation_structure.pk)

                for action in actions:
                    if action.action_type == 'email':
                        # se l'utente ha associato una mail fra le azioni va
                        # inviata
                        current_site = get_current_site(request)
                        site_name = current_site.name
                        domain = current_site.domain
                        context = {
                            'email': action.value,
                            'site': site,
                            'site_name': site_name,
                            'user': user.email,
                            #'token': default_token_generator.make_token(request.user),
                            'protocol': 'https' if request.is_secure() else 'http',
                        }
                        #context_test = {
                        #    'email': 'chiara.oggiano@netfarm.it',
                        #    'site': site,
                        #    'site_name': site_name,
                        #    'user': user.email,
                        #    'token': default_token_generator.make_token(request.user),
                        #    'protocol': 'https' if request.is_secure() else 'http',
                        #}
                        #self.send_mail(context_test, 'chiara.oggiano@netfarm.it')
                        self.send_mail(context, action.value)
                    if action.action_type == 'circle':
                        data = {
                            'text': 'Richiesta di assistenza da %s' % (user.email),
                            'user': user.pk,
                            'circle': [action.circle_id, ]
                        }
                        serializer = PostSerializer(data=data)
                        serializer.is_valid(raise_exception=True)
                        post = serializer.save()
                        # Notifica
                        notifications = Notification.createPostNotifications(
                            user, Notification.Type.CREATE_POST, action.circle, post, pk=post.pk)
                        # se l'utente ha associato uno o piu' gruppi va mandato un messaggio
                        # in bacheca per ogni email nel gruppo
        return Response({'message': 'ok'})


class AssistanceToggleActive(APIView):

    def post(self, request):
        user = request.user

        assistance_id = request.query_params.get('assistance_id', None)
        if assistance_id is None:
            raise ValidationError('Invalid alarm')

        active = request.data.get('handled', None)
        if active is None:
            raise ValidationError('Invalid data')

        try:
            alarm = AssistanceRequest.objects.get(pk=assistance_id)
        except AssistanceRequest.DoesNotExist:
            raise ValidationError('Alarm not found')

        if active == 'true' or active == True:
            alarm.handled = True
            alarm.handler = user
        else:
            alarm.handled = False
            alarm.handler = None

        alarm.save()

        return Response({'message': 'ok'})


class ViewTagsAffiliation(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_id = request.query_params.get('user_id')
        structure_id = request.query_params.get('structure_id')
        try:
            user = UserProfile.objects.get(pk=user_id)
        except UserProfile.DoesNotExist:
            raise ValidationError('User not found')
        try:
            structure = Structure.objects.get(pk=structure_id)
        except Structure.DoesNotExist:
            raise ValidationError('Structure not found')

        affiliation = StructureAffiliation.objects.filter(
                user=user, structure_id__in=[1, structure.pk])

        mymedtags = MyMedTag.objects.filter(
            structure_affiliation__in=affiliation, active=True)

        return Response(MymedtagStructureCOC(instance=mymedtags, many=True).data)

class AssistanceFilter(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user
        '''dateI = request.query_params.get('dateI')
        dateF = request.query_params.get('dateF')
        if dateI:
            alarms = Alarm.objects.filter(date__gte=dateI)
        if dateF:
            alarms = alarms.objects.filter(date__lte=dateF)'''

        alarms = AssistanceRequest.objects.all().order_by('-date')

        return Response(AssistanceRequestSerializer(instance=alarms, many=True).data)

class EditCOCProfileAttributes(APIView):
    permission_classes = (IsAuthenticated, )

    @transaction.atomic
    def put(self, request):
        attributes = request.data.get('data')
        user = request.user

        param_pk = request.query_params.get('guest_id')
        if param_pk:
            try:
                user = UserProfile.objects.get(pk=param_pk)
                # TODO: user devo essere io oppure avere il diritto di
                # modificarne le info
            except UserProfile.DoesNotExist:
                raise ValidationError('User not found')

        if not attributes:
            return Response({'message': 'ok'})

        #user.lifesaver = None

        qs = AttributeValue.objects.filter(user=user)
        coc_request_action = request.query_params.get('coc_request_action', None)
        if coc_request_action is not None:
            qs = qs.filter(attribute__group__structure__id=coc_request_action)
        else:
            qs = qs.exclude(attribute__group__structure__code_type='fast_help')
        qs.delete()

        for new in attributes:
            if new.get('value') is not None:
                # SALVAVITA PRINCIPALE prelevo l'informazione salvavita da
                # aggiungere in un secondo momento al profilo dell'utente
                try:
                    attribute = Attribute.objects.get(
                        pk=new.get('attribute', {}).get('pk'))
                    # lifesaver = new.get('lifesaver', False)
                except Attribute.DoesNotExist:
                    raise ValidationError('Attribute not found')
                else:
                    # l'attributo esiste
                    # l'attributo e' di tipo enum?
                    if attribute.datatype == 'enum':
                        # e' un enum
                        found_enums = Enum.objects.filter(
                            pk__in=new.get('value'))
                        if found_enums.count() != len(new.get('value')):
                            raise ValidationError('Enums not found')

                        # l'array di id relativi agli enum scelti li passo
                        # tutti insieme perche e' la create_attribute_value che
                        # li gestisce
                        attributevalue = AttributeValue.objects.create_attribute_value(
                            value=new.get('value'),
                            user=user,
                            attribute=attribute,
                            lifesaver=new.get('lifesaver', False))
                    else:
                        # boolean,text,number...
                        attributevalue = AttributeValue.objects.create_attribute_value(
                            value=new.get('value'),
                            user=user,
                            attribute=attribute,
                            lifesaver=new.get('lifesaver', False))

            # if new.get('lifesaver_main'):
                # user.lifesaver = None
                # user.save()
        print user.pk
        return Response({'message': 'ok'})
