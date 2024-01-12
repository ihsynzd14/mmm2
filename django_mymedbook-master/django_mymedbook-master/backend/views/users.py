from django.db import transaction

from django.contrib.auth import authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model
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

from datetime import datetime
import urllib

def send_mail(self, context, to_email):
    print 'SEND_MAIL'
    subject = subject
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    body = context

    email_message = EmailMultiAlternatives(subject, body, None, [to_email])
    email_message.send()


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit_elem'
    max_page_size = 10
    paginate_by = 10


class UploadProfile(APIView):
    permission_classes = (IsAuthenticated, )
    parser_classes = (FileUploadParser, MultiPartParser)

    def post(self, request):
        upload = request.data['file']
        guest = request.data['file']
        field = request.user.avatar

        handle_upload(field, upload, MEDIA_AVATAR)

        context = {'request': request}
        utente = UserProfileSerializer(
            context=context, instance=request.user).data
        return Response(utente)


class UploadGuest(APIView):
    permission_classes = (IsAuthenticated, )
    parser_classes = (FileUploadParser, MultiPartParser)

    def post(self, request):
        upload = request.data['file']
        guest_id = request.query_params.get('guest_id')
        if guest_id:
            try:
                user = UserProfile.objects.get(pk=guest_id)
            except UserProfile.DoesNotExist:
                raise NotFound('guest not found')

        field = user.avatar

        handle_upload(field, upload, MEDIA_AVATAR)

        context = {'request': request}
        utente = UserProfileSerializer(
            context=context, instance=user).data
        return Response(utente)


class EditProfileAttributes(APIView):
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

        # added
        # added_data = attributes.get('added', None)
        # if added_data is not None:
        #    for item in added_data:
        #        attribute_instance = Attribute.objects.get(pk=attribute.get('pk'))
                # sono enum
        #        if len(item.value)>0:
        #            for value in item.value:
        #                attribute_instance = Attribute.objects.get(pk=attribute.get('pk'))
        # modified
        # modified_data = attributes.get('modified')

        # removed
        # removed_data = attributes.get('removed')
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
                    elif attribute.datatype == 'year_with_text':
                        attributevalue = AttributeValue.objects.create_attribute_value(
                            value=new.get('value'),
                            user=user,
                            attribute=attribute,
                            other=new.get('other',None),
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


class EditProfile(APIView):
    permission_classes = (IsAuthenticated, )

    def put(self, request):
        data = request.data.get('data')
        data.pop('username', '')
        data.pop('email', '')
        #data.pop('lifesaver', '')
        user = request.user

        param_pk = request.query_params.get('guest_id')
        if param_pk:
            try:
                user = UserProfile.objects.get(pk=param_pk)
            except UserProfile.DoesNotExist:
                raise ValidationError('User not found')

        user = UserProfileSerializer(instance=user, data=data, partial=True)
        user.is_valid(raise_exception=True)
        user = user.save()

        return Response(UserProfileSerializer(instance=user).data)


class VerificationGuestExistence(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user

        guest_email = request.query_params.get('email')
        try:
            guest = UserProfile.objects.get(email=guest_email)
        except UserProfile.DoesNotExist:
            raise NotFound("User not found")
        else:
            message = UserProfileSerializer(instance=guest).data

        return Response(message)


class VerificationAffiliation(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user

        # TODO verificare se l'utente autenticato e' un operatore sanitario
        struttura = request.query_params.get('structure_id')
        guest_id = request.query_params.get('id')
        try:
            guest = UserProfile.objects.get(pk=guest_id)
        except UserProfile.DoesNotExist:
            raise NotFound('User not found')

        try:
            guest = StructureAffiliation.objects.get(
                structure_pk=struttura, affiliation_ptr__user=guest_id)
        except StructureAffiliation.DoesNotExist:
            raise NotFound("Affiliation not found")
        else:
            message = {'message': 'ok'}

        return Response(message)


class UsersAffiliationsList(APIView):
    permission_classes = (IsAuthenticated, )
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        structure_id = request.query_params.get('structure_id')

        try:
            structure = Structure.objects.get(pk=structure_id)
        except Structure.DoesNotExist:
            raise ValidationError('Structure not found')

        affiliations = StructureAffiliation.objects.filter(
            structure=structure, left=None)
        members = []

        for affiliation in affiliations:
            user = UserProfile.objects.get(pk=affiliation.user_id)
            members.append(UserProfileMinimalSerializer(instance=user).data)

        return Response(members)


class UserAffiliationSingle(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user
        guest_id = request.query_params.get('user_id')

        try:
            guest = UserProfile.objects.get(pk=int(guest_id))
        except UserProfile.DoesNotExist:
            raise ValidationError('User not found')

        return Response(UserProfileSerializer(instance=guest).data)


class DeactiveAffiliation(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user
        structure_id = request.query_params.get('structure_id')
        guest_id = request.query_params.get('user_id')

        try:
            structure = Structure.objects.get(pk=structure_id)
        except Structure.DoesNotExist:
            raise ValidationError('Structure not found')

        try:
            guest = UserProfile.objects.get(pk=guest_id)
        except UserProfile.DoesNotExist:
            raise ValidationError('Guest not found')

        try:
            affiliation = StructureAffiliation.objects.get(
                user=guest, structure=structure)
        except StructureAffiliation.DoesNotExist:
            raise ValidationError('Guest not found')

        #cancella l'affiliazione alle sue cerchie e le cerchie che ha creato
        '''guest.circleaffiliation_set = None
        his_circles = Circle.objects.filter(created_by=guest)
        for his_circle in his_circles:
            his_circle.delete()'''

        affiliation.left = datetime.now()
        affiliation.save()

        return Response({'message': 'ok'})


class VerificationMembership(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user

        # TODO verificare se l'utente autenticato e' un operatore sanitario
        structure_id = request.query_params.get('structure_id')
        guest = UserProfile.objects.get(pk=request.query_params.get('user_id'))

        try:
            structure = Structure.objects.get(pk=structure_id)
        except Structure.DoesNotExist:
            raise NotFound('Structure not found')

        try:
            guest = StructureMembership.objects.get(
                structure=structure, user=guest)
        except StructureMembership.DoesNotExist:
            raise NotFound("Membership not found")
        else:
            message = {'message': 'ok'}

        return Response(message)

## REGISTRAZIONE OSPITE ##


class SaveAffiliation(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        data = request.data

        # TODO verificare se l'utente autenticato e' un operatore sanitario
        try:
            struttura = Structure.objects.get(pk=data.get('structure_id'))
        except Structure.DoesNotExist:
            raise NotFound('Structure not found')

        guest = StructureAffiliation.objects.create(
            structure=struttura, user=data.get('guest_id'))

        return Response({'message': 'ok'})

## REGISTRAZIONE DIPENDENTE ##


class newMembership(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):

        try:
            group = Group.objects.get(pk=request.data.pop('group'))
        except KeyError, Group.DoesNotExist:
            raise NotFound('Group not found')

        try:
            structure = Structure.objects.get(pk=request.data.pop('structure'))
        except KeyError, Structure.DoesNotExist:
            raise NotFound('Structure not found')

        data = request.data.copy()

        data['username'] = data['email']
        data['registered_by'] = request.user

        with transaction.atomic():
            serialized = UserProfileSerializer(data=data)
            serialized.is_valid(raise_exception=True)
            user = serialized.save()

            group.user_set.add(user)

            StructureMembership.objects.create(user=user, structure=structure)
            structure_mymedbook = Structure.objects.get(name='mymedbook')
            StructureAffiliation.objects.create(
                user=user, structure=structure_mymedbook)

            tag = 'dipendenti_%s' % structure.label
            InterestedTag.objects.create(email=data['email'], tag=tag)

            # creazione di un gruppo familiari, se non esiste gia'
            #TODO: se operatore sanitario o portiere non fa parte del gruppo
            if request.user.groups in ['animatore_cdv', 'direttore_cdv' ]:
                try:
                    circle_familiari = Circle.objects.get(name="Familiari Ospiti")
                except Circle.DoesNotExist:
                    circle_familiari = Circle.objects.create(
                        name="Familiari Ospiti",
                        created_by=request.user,
                        read_only=True
                    )
                    CircleAffiliation.objects.create(
                        circle=circle_familiari,
                        user=user,
                        email=user.email
                    )
            try:
                circle_dipendenti = Circle.objects.get(name="Dipendenti_CDV")
            except Circle.DoesNotExist:
                circle_dipendenti = Circle.objects.create(
                    name="Dipendenti_CDV",
                    created_by=request.user
                )
            CircleAffiliation.objects.create(
                circle=circle_dipendenti,
                user=user,
                email=user.email
            )
            # creazione di un dossier medico
            Dossier.objects.create(
                name='%s_%s' % (user.username, user.fiscal_code),
                user=user
            )
            ''' tag = 'utente_MMB'
            InterestedTag.objects.create(email=data['email'], tag=tag)'''

        return Response(serialized.data)

class addAffiliationParent(APIView):
    permission_classes = (IsAuthenticated, )
    subject_template_name = 'registration/activation_account.txt'
    email_template_name = 'registration/activation_account.html'

    def get(self, request):

        guest_id = request.query_params.get('guest')
        parent_id = request.query_params.get('parent')
        structure_id = request.query_params.get('structure_id')

        try:
            guest = UserProfile.objects.get(pk=guest_id)
        except UserProfile.DoesNotExist:
            raise ValidationError('Guest not found')
        try:
            user = UserProfile.objects.get(pk=parent_id)
        except UserProfile.DoesNotExist:
            raise ValidationError('Guest not found')
        try:
            structure = Structure.objects.get(pk=structure_id)
        except KeyError, Structure.DoesNotExist:
            raise NotFound('Structure not found')

        with transaction.atomic():
            tag = 'familiari_%s' % structure.label
            InterestedTag.objects.create(email=user.email, tag=tag)

            info_guest = "%s_%s_%s" % (
                guest.first_name, guest.last_name, str(guest.birthday))
            # gruppo familiare_ospite per CDV
            try:
                circle = Circle.objects.get(name="Gruppo_ospite_%s" % info_guest)
            except Circle.DoesNotExist:
                # se non c'e' creo un gruppo familiare per l'ospite passato
                # dove inseriamo l'ospite, il direttore, gli animatori e il
                # familiare
                circle = Circle.objects.create(
                    name="Gruppo_ospite_%s" % info_guest,
                    created_by=guest
                )
                partecipants = UserProfile.objects.filter(
                    Q(groups__name__in=['direttore_cdv']) |
                    Q(groups__name__in=['animatore_cdv'])
                )
                for partecipant in partecipants:
                    CircleAffiliation.objects.create(
                        circle=circle,
                        user=partecipant,
                        email=partecipant.email
                    )
                CircleAffiliation.objects.create(
                    circle=circle,
                    user=guest,
                    email=guest.email
                )

            CircleAffiliation.objects.create(
                circle=circle,
                user=user,
                email=user.email
            )
            # associazione al gruppo familiari Ospiti di CDV
            try:
                circle_guest = Circle.objects.get(name="Familiari Ospiti")
            except Circle.DoesNotExist:
                raise ValidationError('Familiari Ospiti does not exist')
            # esiste gia' un gruppo Familiari associato all'ospite, allora
            # inserisco solo l'associazione con il familiare
            else:
                CircleAffiliation.objects.create(
                    circle=circle_guest,
                    user=user,
                    email=user.email
                )
        return Response({'message':'ok'})

class newAffiliationParent(APIView):
    permission_classes = (IsAuthenticated, )
    subject_template_name = 'registration/activation_account.txt'
    email_template_name = 'registration/activation_account.html'

    def send_mail(self, context, to_email):
        subject = loader.render_to_string(self.subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(self.email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, None, [to_email])
        email_message.send()

    def post(self, request):
        data = request.data.copy()
        #TODO: da eliminare
        data['active']=True
        guest_id = data.pop('guest')

        data['username'] = data['email']
        data['registered_by'] = request.user

        try:
            structure = Structure.objects.get(pk=request.data.pop('structure'))
        except KeyError, Structure.DoesNotExist:
            raise NotFound('Structure not found')

        with transaction.atomic():
            serialized = UserProfileSerializer(data=data)
            serialized.is_valid(raise_exception=True)
            user = serialized.save()

            structure_mymedbook = Structure.objects.get(name='mymedbook')
            StructureAffiliation.objects.create(
                user=user, structure=structure_mymedbook)

            tag = 'familiari_%s' % structure.label
            InterestedTag.objects.create(email=data['email'], tag=tag)

            # prendo il profilo dell'ospite
            try:
                guest = UserProfile.objects.get(pk=guest_id)
            except UserProfile.DoesNotExist:
                raise ValidationError("User not found")

            info_guest = "%s_%s_%s" % (
                guest.first_name, guest.last_name, str(guest.birthday))
            # gruppo familiare_ospite per CDV
            try:
                circle = Circle.objects.get(name="Gruppo_Ospite_%s" % info_guest)
            except Circle.DoesNotExist:
                # se non c'e' creo un gruppo familiare per l'ospite passato
                # dove inseriamo l'ospite, il direttore, gli animatori e il
                # familiare
                circle = Circle.objects.create(
                    name="Gruppo_Ospite_%s" % info_guest,
                    created_by=guest
                )
                partecipants = UserProfile.objects.filter(
                    Q(groups__name__in=['direttore_cdv']) |
                    Q(groups__name__in=['animatore_cdv'])
                )
                for partecipant in partecipants:
                    CircleAffiliation.objects.create(
                        circle=circle,
                        user=partecipant,
                        email=partecipant.email
                    )
                CircleAffiliation.objects.create(
                    circle=circle,
                    user=guest,
                    email=guest.email
                )

            CircleAffiliation.objects.create(
                circle=circle,
                user=user,
                email=user.email
            )
            # associazione al gruppo familiari Ospiti di CDV
            try:
                circle_guest = Circle.objects.get(name="Familiari Ospiti")
            except Circle.DoesNotExist:
                raise ValidationError('Familiari Ospiti does not exist')
            # esiste gia' un gruppo Familiari associato all'ospite, allora
            # inserisco solo l'associazione con il familiare
            else:
                CircleAffiliation.objects.create(
                    circle=circle_guest,
                    user=user,
                    email=user.email
                )

            # associazione al gruppo familiare dell'ospite
            '''try:
                circle_guest = Circle.objects.get(created_by=guest_id)
            except Circle.DoesNotExist:
                # se non esiste ancora per l'ospite un gruppo familiari, lo
                # creiamo e ci inseriamo il familiare
                circle_parent_guest = Circle.objects.create(
                    name="Familiari",
                    created_by=guest
                )
                CircleAffiliation.objects.create(
                    circle=circle_parent_guest,
                    user=user,
                    email=user.email
                )
            # esiste gia' un gruppo Familiari associato all'ospite, allora
            # inserisco solo l'associazione con il familiare
            else:
                CircleAffiliation.objects.create(
                    circle=circle_guest,
                    user=user,
                    email=user.email
                )'''

            # creazione per il familiare di un gruppo con la mail del direttore
            '''circle_direttore = Circle.objects.create(
                name="Direttore_CDV_%s" % user.email,
                created_by=request.user
            )
            # creazione per il familiare di un gruppo con la mail degli animatori
            circle_animatori = Circle.objects.create(
                name="Animatori_CDV_%s" % user.email,
                created_by=request.user
            )'''
            # circle affiliation con il familiare, con il direttore e con gli
            # animatori
            '''CircleAffiliation.objects.create(
                circle=circle_direttore,
                user=user,
                email=user.email
            )
            for dirett in UserProfile.objects.filter(groups__name__in=['direttore_CDV']):
                CircleAffiliation.objects.create(
                    circle = circle_animatori,
                    user = dirett,
                    email = user.email
                )
                # circle affiliation per il direttore con il familiare
                # direttore = UserProfile.objects.get(group="direttore_CDV")
                CircleAffiliation.objects.create(
                    circle=circle_direttore,
                    user=dirett,
                    email= dirett.email
                )
            # circle affiliation per gli animatori con il familiare
            for animatore in UserProfile.objects.filter(groups__name__in=["animatore_CDV"]):
                CircleAffiliation.objects.create(
                    circle=circle_animatori,
                    user=animatore,
                    email=animatore.email
                )
            '''
            # creazione di un dossier medico
            Dossier.objects.create(
                name="%s_%s" % (user.email, user.first_name),
                user=user
            )


            # MAIL DI ATTIVAZIONE
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain

            context = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'user': user,
                'protocol': 'https' if request.is_secure() else 'http',
                'activate_account': '/users/activate_account/'
            }

            self.send_mail(context, user.email)

            return Response(serialized.data)


class change_password(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        try:
            old_password = request.data.pop('old_password')
            new_password = request.data.pop('new_password')
        except KeyError:
            raise ValidationError({'detail': 'Invalid arguments'})

        user = authenticate(username=request.user.username,
                            password=old_password)
        if user is None:
            raise ValidationError({'detail': 'Invalid password'})

        validate_password(new_password, user)
        user.plaintext_password = new_password
        user.set_password(new_password)
        user.save()

        return Response({'message': 'ok'})

class UsersListForChat(APIView):
    def get(self, request):
        user = request.user
        groups = Circle.objects.filter(circleaffiliation__user=user)
        usersList = []
        for group in groups:
            affiliations = CircleAffiliation.objects.filter(circle=group).distinct('user')
            for affiliation in affiliations:
                if affiliation.user not in usersList:
                    if affiliation.user and affiliation.user.pk!=request.user.pk:
                        usersList.append(affiliation.user)
        return Response(UserProfileMinimalSerializer(instance=usersList, many=True).data)

class UserActivateAccount(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        try:
            user = UserProfile.objects.get(pk=user_id)
        except UserProfile.DoesNotExist:
            raise ValidationError('User not found')
        user.active=True
        user.save()

        return Response({'message':'ok'})

class sendMailActivation(APIView):
    subject_template_name = 'registration/activation_account.txt'
    email_template_name = 'registration/activation_account.html'

    def send_mail(self, context, to_email):
        subject = loader.render_to_string(self.subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(self.email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, None, [to_email])
        #email_message.attach_alternative(body, "text/html")
        html_content = body
        email_message.attach_alternative(html_content, "text/html")
        email_message.send()

    def get(self, request):
        try:
            user = UserProfile.objects.get(email=request.query_params.get('email', None))
        except UserProfile.DoesNotExist:
            raise ValidationError('User not found')

        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain

        context = {
            'email': user.email,
            'domain': domain,
            'site_name': site_name,
            'user': user,
            'protocol': 'https' if request.is_secure() else 'http',
            'activate_account': '/password/activate.html'
        }

        self.send_mail(context, user.email)
        return Response({'message':'ok'})
