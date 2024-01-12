from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q, Value
from django.template import loader
from django.db import transaction
from django.contrib.sites.shortcuts import get_current_site

from rest_framework import status, permissions, routers, serializers, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.pagination import PageNumberPagination

from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope, TokenHasScope

from collections import OrderedDict

from backend.models import *
from backend.utils import *
from device.models import Device, Notification
from datetime import datetime, timedelta
import operator

import pytz

User = get_user_model()


def send_mail(self, subject, context, to_email):
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


class AllFieldsSerializer(serializers.ModelSerializer):

    def get_fields(self):
        original_fields = super(AllFieldsSerializer, self).get_fields()
        fields = OrderedDict()
        for k, v in original_fields.items():
            fields['pk' if k == 'id' else k] = v
        return fields


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'


class GroupSmallSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ('name', )


class GroupViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = ['groups']
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class StructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Structure
        fields = (
            'pk',
            'name',
            'max_members',
            'max_affiliates',
            'mobile_number',
            'phone_number',
            'code_type',
            'created',
            'modified'
        )
        readonly_fields = ('created', 'modified')


class StructureViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = Structure.objects.all()
    serializer_class = StructureSerializer


class AttributeGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttributeGroup
        fields = (
            'pk',
            'name',
            'structure',
            'created',
            'modified'
        )
        readonly_fields = ('created', 'modified')


class AttributeGroupViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = AttributeGroup.objects.all()
    serializer_class = AttributeGroupSerializer


class AttributeSerializer(AllFieldsSerializer):

    class Meta:
        model = Attribute
        exclude = ('forced_lifesaver', 'sorting')
        readonly_fields = ('created', 'modified')


class AttributeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer


class EnumSerializer(serializers.ModelSerializer):

    class Meta:
        model = Enum
        fields = (
            'pk',
            'value',
            'attribute',
            'created',
            'modified'
        )
        readonly_fields = ('created', 'modified')


class EnumViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = Enum.objects.all()
    serializer_class = EnumSerializer


class ProductTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductType
        fields = (
            'pk',
            'name',
            'created',
            'modified'
        )
        readonly_fields = ('created', 'modified')


class ProductTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer


class MyMedTagSerializer(serializers.ModelSerializer):
    product_type = ProductTypeSerializer(read_only=True)

    class Meta:
        model = MyMedTag
        fields = (
            'pk',
            'code',
            'product_type',
            'active',
            'created',
            'modified'
        )
        readonly_fields = ('created', 'modified')

class MymedtagStructure(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = MyMedTag.objects.filter(active=True).all()
    serializer_class = MyMedTagSerializer

    def create(self, request):

        with transaction.atomic():
            # Se esistun tag con lo stesso codice e attivo manda errore
            code = request.data.get('code')

            mymedtag = MyMedTag.objects.filter(code=code, active=True)
            if mymedtag.count()>0:
                raise ValidationError({'detail': 'Tag gia\' in uso'})
            try:
                # Se esiste gia' un tag, lo disattiva e ne crea uno nuovo
                pk = request.data.pop('pk')
                mymedtag = MyMedTag.objects.get(pk=pk)
                mymedtag.active = False
                mymedtag.save()
            except KeyError, MyMedTag.DoesNotExist:
                pass

        serialized = MyMedTagSerializer(data=request.data, partial=True)
        serialized.is_valid(raise_exception=True)
        sa=None
        try:
            sa = StructureAffiliation.objects.get(pk=request.data.pop(
                'structure_affiliation'), structure__id=request.data.pop('structure_id'))
        except KeyError, StructureAffiliation.DoesNotExist:
            try:
                sa = StructureMembership.objects.get(pk=request.data.pop(
                    'structure_membership'), structure__id=request.data.pop('structure_id'))
            except StructureMembership.DoesNotExist:
                raise KeyError, NotFound('Affiliation or Membership not found')
            else:
                serialized.save(structure_membership=sa)
        else:
            serialized.save(structure_affiliation=sa)

        return Response(serialized.data)


class MyMedTagViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = MyMedTag.objects.all()
    serializer_class = MyMedTagSerializer

    def list(self, request):
        mymedtags = MyMedTag.objects.filter(
            active=True, structure_affiliation__user=request.user)
        return Response(MyMedTagSerializer(instance=mymedtags, many=True).data)

    def create(self, request):
        try:
            sa = StructureAffiliation.objects.get(
                user=request.user, structure__name='mymedbook')
        except StructureAffiliation.DoesNotExist:
            raise NotFound('Affiliation not found')

        with transaction.atomic():
            # Sto modificando un tag mi arriva il pk
            pk = request.data.pop('pk', None)
            if pk is not None:
                try:
                    mymedtag = MyMedTag.objects.get(pk=pk)
                    mymedtag.active = False
                    mymedtag.save()
                except KeyError, MyMedTag.DoesNotExist:
                    pass
            else:
                # controllo che il codice che mi arriva sia gia' presente, in
                # caso se attivo non faccio nulla e se disattivo vado alla
                # creazione di uno nuovo
                code = request.data.get('code')
                if code is not None:
                    mymedtag = MyMedTag.objects.filter(
                        code=code, structure_affiliation__user=request.user)
                    for tag in mymedtag:
                        if tag.active == True:
                            raise ValidationError(
                                {'detail': 'Tag gia\' presente'})

            serialized = MyMedTagSerializer(data=request.data, partial=True)
            serialized.is_valid(raise_exception=True)

            try:
                product = request.data.pop('product_type')
                product_type = ProductType.objects.get(pk=product['pk'])
            except KeyError, ProductType.DoesNotExist:
                serialized.save(structure_affiliation=sa)
            else:
                serialized.save(product_type=product_type,
                                structure_affiliation=sa)
            return Response(serialized.data)

    def get_queryset(self):
        return MyMedTag.objects.filter(structure_affiliation__user=self.request.user.pk, active=True)

    def update(self, request, pk):
        '''
            Da rivedere in quanto vanno gestiti i permessi.
            Solo gli operatori possono effettuare questa modifica
        '''
        return super(MyMedTagViewSet, self).update(request, pk=pk, partial=True)

    def destroy(self, request, pk):
        '''
            La delete e' intesa come modifica del campo left con la data odierna
        '''
        structMemb = MyMedTag.objects.get(pk=pk)
        structMemb.active = False
        structMemb.save()
        return Response({'message': 'ok'})


class StructureAffiliationSerializer(serializers.ModelSerializer):
    structure = StructureSerializer()
    mymedtag_set = serializers.SerializerMethodField()  # MyMedTagSerializer(many=True)

    def get_mymedtag_set(self, obj):
        return MyMedTagSerializer(instance=obj.mymedtag_set.filter(active=True), many=True).data

    class Meta:
        model = StructureAffiliation
        fields = (
            'pk',
            'joined',
            'left',
            'user',
            'structure',
            'mymedtag_set',
            'created',
            'modified'
        )
        readonly_fields = ('created', 'modified')


class StructureAffiliationViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = StructureAffiliation.objects.all()
    serializer_class = StructureAffiliationSerializer

    def update(self, request, pk):
        '''
            Da rivedere in quanto vanno gestiti i permessi.
            Solo gli operatori possono effettuare questa modifica
        '''
        return super(StructureAffiliationViewSet, self).update(request, pk=pk, partial=True)

    def create(self, request):
        data = request.data

        # TODO verificare se l'utente autenticato e' un operatore sanitario"
        try:
            struttura = Structure.objects.get(pk=data.get('structure_id'))
        except Structure.DoesNotExist:
            raise NotFound('Structure not found')
        try:
            user = UserProfile.objects.get(pk=data.get('guest_id'))
        except UserProfile.DoesNotExist:
            raise NotFound('Guest not found')

        guest = StructureAffiliation.objects.create(
            structure=struttura, user=user)

        return Response({'message': 'ok'})

    def get_queryset(self):

        structure_id = self.request.query_params.get('structure_id')
        if structure_id:
            try:
                structure = Structure.objects.get(pk=structure_id)
            except Structure.DoesNotExist:
                raise NotFound('Structure not found')

            queryset = StructureAffiliation.objects.filter(structure=structure)
        else:
            queryset = StructureAffiliation.objects.all()

        member_id = self.request.query_params.get('user_id')
        if member_id is not None:
            try:
                member = UserProfile.objects.get(pk=member_id)
            except UserProfile.DoesNotExist:
                raise NotFound('User not found')

            queryset = queryset.filter(user=member)

        return queryset


class StructureMembershipSerializer(serializers.ModelSerializer):
    structure = StructureSerializer()
    mymedtag_set = serializers.SerializerMethodField()  # MyMedTagSerializer(many=True)

    def get_mymedtag_set(self, obj):
        return MyMedTagSerializer(instance=obj.mymedtag_set.filter(active=True), many=True).data

    class Meta:
        model = StructureMembership
        fields = (
            'pk',
            'joined',
            'left',
            'user',
            'structure',
            'mymedtag_set',
            'created',
            'modified'
        )
        readonly_fields = ('created', 'modified')


class StructureMembershipViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = StructureMembership.objects.all()
    serializer_class = StructureMembershipSerializer

    def update(self, request, pk):
        '''
            Da rivedere in quanto vanno gestiti i permessi.
            Solo gli operatori possono effettuare questa modifica
        '''
        return super(StructureMembershipViewSet, self).update(request, pk=pk, partial=True)

    def create(self, request):
        data = request.data

        # TODO verificare se l'utente autenticato e' un operatore sanitario"
        try:
            struttura = Structure.objects.get(pk=data.get('structure_id'))
        except Structure.DoesNotExist:
            raise NotFound('Structure not found')
        try:
            user = UserProfile.objects.get(pk=data.get('user_id'))
        except UserProfile.DoesNotExist:
            raise NotFound('Guest not found')

        guest = StructureMembership.objects.create(
            structure=struttura, user=user)

        return Response({'message': 'ok'})

    def get_queryset(self):

        structure = self.request.query_params.get('structure_id')
        if structure:
            try:
                structure = Structure.objects.get(pk=structure)
            except Structure.DoesNotExist:
                raise NotFound('Structure not found')

            queryset = StructureMembership.objects.filter(structure=structure)
        else:
            queryset = StructureMembership.objects.all()

        member_id = self.request.query_params.get('user_id')
        if member_id is not None:
            try:
                member = UserProfile.objects.get(pk=member_id)
            except UserProfile.DoesNotExist:
                raise NotFound('User not found')

            queryset = queryset.filter(user=member)

        return queryset

    def destroy(self, request, pk):
        '''
            La delete e' intesa come modifica del campo left con la data odierna
        '''
        structMemb = StructureMembership.objects.get(pk=pk)
        structMemb.left = datetime.today().strftime('%Y-%m-%d')
        structMemb.save()
        return Response({'message': 'ok'})


class UserProfileSerializerForAdmin(serializers.ModelSerializer):
    pagination_class = StandardResultsSetPagination

    class Meta:
        model = UserProfile
        fields = (
            'pk',
            'first_name',
            'last_name',
            'email',
            'phone',
            'active',
            'plaintext_password',
            'created',
            'modified'
        )


class UserProfileForAdminViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser, )
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializerForAdmin
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return UserProfile.objects.filter(structureaffiliation__structure__name='mymedbook').exclude(
            structuremembership__structure__name='CDV').exclude(structureaffiliation__structure__name='CDV').order_by('-created')

class AttributeValueSerializer(AllFieldsSerializer):
    value = serializers.SerializerMethodField()
    other = serializers.SerializerMethodField()
    attribute = AttributeSerializer(read_only=True)

    class Meta:
        model = AttributeValue
        exclude = ('text_value', 'boolean_value', 'number_value', 'enum', 'date_value')
        readonly_fields = ('created', 'modified')

    def get_value(self, obj):
        return unicode(obj) or u''

    def get_other(self, obj):
        return unicode(obj.text_value) or u''

class UserProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    avatar = serializers.ImageField(
        max_length=None, use_url=False, read_only=True,
    )
    groups = GroupSmallSerializer(read_only=True, many=True)
    structuremembership_set = StructureMembershipSerializer(
        read_only=True, many=True)
    structureaffiliation_set = StructureAffiliationSerializer(
        read_only=True, many=True)

    class Meta:
        model = UserProfile
        fields = (
            'pk',
            'first_name',
            'last_name',
            'username',
            'email',
            'birthday',
            'fiscal_code',
            'sex',
            'phone',
            'town',
            'height',
            'weight',
            'bmi',
            'password',
            'plaintext_password',
            'avatar',
            'active',
            'groups',
            'lifesaver',
            'is_staff',
            'public_lifesaver',
            'structureaffiliation_set',
            'structuremembership_set',
            'created',
            'modified'
        )
        readonly_fields = (
            'password',
            'plaintext_password',
            'created',
            #'lifesaver',
            'modified',
            'active')

    def create(self, validated_data):
        data = validated_data.copy()
        data['username'] = data['email']
        user = super(UserProfileSerializer, self).create(data)
        password = validated_data.pop('password', None)

        if password:
            user.set_password(password)
            user.plaintext_password = password
            user.save()

        return user


class RegisterViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
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

    def create(self, request):
        data = request.data.copy()
        data['username'] = data.get('email')
        #data['active'] = True
        attributes = data.pop('attributes', None)
        structure_id = data.pop('structure_id', None)

        with transaction.atomic():
            if request.user.is_anonymous():
                #data['active'] = True
                serialized = UserProfileSerializer(data=data)
                serialized.is_valid(raise_exception=True)
                user = serialized.save()

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
            else:
                data['active'] = True
                serialized = UserProfileSerializer(data=data)
                serialized.is_valid(raise_exception=True)
                user = serialized.save()
            try:
                structureMMB = Structure.objects.get(name='mymedbook')
            except Structure.DoesNotExist:
                raise ValidationError('Structure mymedbook not found')

            sa = StructureAffiliation.objects.create(
                structure=structureMMB,
                user=user
            )

            if request.user.is_authenticated() and structure_id is not None:
                try:
                    structure = Structure.objects.get(pk=structure_id)
                except Structure.DoesNotExist:
                    raise ValidationError('Structure not found')

                sa = StructureAffiliation.objects.create(
                    structure=structure,
                    user=user
                )

                if structure.code_type=='RSA':
                    birthday = ''
                    if user.birthday:
                        birthday = str(user.birthday)
                    info_guest = "%s_%s_%s" % (
                        user.first_name, user.last_name, birthday)
                    # gruppo familiare_ospite per CDV
                    try:
                        circle = Circle.objects.get(
                            name="Gruppo_ospite_%s" % info_guest)
                    except Circle.DoesNotExist:
                        # se non c'e' creo un gruppo familiare per l'ospite passato
                        # dove inseriamo l'ospite, il direttore, gli animatori e il
                        # familiare
                        circle = Circle.objects.create(
                            name="Gruppo_ospite_%s" % info_guest,
                            created_by=user
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
                            user=user,
                            email=user.email
                        )
                if structure.code_type=='fast_help':
                    user.public_lifesaver = True
                    user.save()
            if attributes:
                AttributeValue.create_user_attributes(user, attributes)

            # creazione di un gruppo familiari

            circle = Circle.objects.create(
                name="Familiare_%s" % (user.first_name),
                created_by=user,
            )
            CircleAffiliation.objects.create(
                circle=circle,
                user_id=user.pk,
                email=user.email
            )
            #se la mail appartiene gia ad un gruppo voglio creare un affiliazione
            circles_common = CircleAffiliation.objects.filter(email=user.email, user__isnull=True)
            for circle_common in circles_common:
                circle_common.user_id=user.pk
                circle_common.save()

            # creazione di un dossier medico
            Dossier.objects.create(
                name="%s_%s" % (user.email, user.first_name),
                user_id=user.pk
            )
        return Response(serialized.data)


class AttributeValueViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = AttributeValue.objects.all()
    serializer_class = AttributeValueSerializer


class UserProfileMinimalSerializer(UserProfileSerializer):
    avatar = serializers.ImageField(
        max_length=None, use_url=False, read_only=True,)
    structureaffiliation_set = StructureAffiliationSerializer(
        read_only=True, many=True)
    structuremembership_set = StructureAffiliationSerializer(
        read_only=True, many=True)

    class Meta:
        model = UserProfile
        fields = (
            'pk',
            'first_name',
            'last_name',
            'structureaffiliation_set',
            'structuremembership_set',
            'email',
            'phone',
            'avatar',
            'groups',
            'created',
            'modified'
        )


class UserProfileMymedbookSerializer(UserProfileSerializer):
    avatar = serializers.ImageField(
        max_length=None, use_url=False, read_only=True,)

    class Meta:
        model = UserProfile
        fields = (
            'pk',
            'first_name',
            'last_name',
            'groups',
            'phone',
            'avatar',
            'created',
            'modified'
        )


class UserProfileCDVSerializer(UserProfileSerializer):
    avatar = serializers.ImageField(
        max_length=None, use_url=False, read_only=True,)

    class Meta:
        model = UserProfile
        fields = (
            'pk',
            'first_name',
            'last_name',
            'birthday',
            'avatar',
            'groups',
            'created',
            'modified'
        )


class UserProfileViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def list(self, request):
        context = {'request': request}
        return Response(UserProfileSerializer(instance=request.user).data)

    def update(self, request, pk):
        if request.POST.get('email', ''):
            return Response({'message': 'Is not possible to edit the email'})

        data = request.data

        serializer = UserProfileSerializer(
            instance=request.user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserProfileSerializer(instance=request.user).data)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):

        queryset = UserProfile.objects.all()

        try:
            structure = Structure.objects.get(
                pk=self.request.query_params.get('structure_id'))
        except Structure.DoesNotExist:
            pass

        if self.request.query_params.get('members'):
            queryset = UserProfile.objects.filter(
                Q(structuremembership__structure=structure, structuremembership__left=None))
        if self.request.query_params.get('affiliations'):
            queryset = UserProfile.objects.filter(
                Q(structureaffiliation__structure=structure, structureaffiliation__left=None))

        email = self.request.query_params.get('email', None)
        if email is not None:
            try:
                user = UserProfile.objects.get(
                    email=email)
            except UserProfile.DoesNotExist:
                raise NotFound('User not found')
            queryset = queryset.filter(pk=user.id)

        ##### RICERCA ######
        path = self.request.query_params.get('path')
        if path:
            path = path.split()
            qset1 = reduce(operator.__and__, [
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(username__icontains=query) |
                Q(structureaffiliation__mymedtag__code__icontains=query) for query in path
            ])

            queryset = queryset.filter(qset1).distinct()

        user_id = self.request.query_params.get('user_id', None)
        if user_id is not None:
            try:
                user = UserProfile.objects.get(
                    pk=user_id)
            except UserProfile.DoesNotExist:
                raise NotFound('User not found')
            queryset = queryset.filter(pk=user.pk).order_by(
                'groups', 'last_name', 'first_name')
        else:
            queryset = queryset.order_by('last_name', 'first_name', 'email')

        return queryset


class AllUserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    # pagination_class = StandardResultsSetPagination

    def get_queryset(self):

        queryset = UserProfile.objects.all()

        try:
            structure = Structure.objects.get(
                pk=self.request.query_params.get('structure_id'))
        except Structure.DoesNotExist:
            pass

        if self.request.query_params.get('members'):
            queryset = UserProfile.objects.filter(
                Q(structuremembership__structure=structure, structuremembership__left=None))
        if self.request.query_params.get('affiliations'):
            queryset = UserProfile.objects.filter(
                Q(structureaffiliation__structure=structure, structureaffiliation__left=None))

        email = self.request.query_params.get('email', None)
        if email is not None:
            try:
                user = UserProfile.objects.get(
                    email=email)
            except UserProfile.DoesNotExist:
                raise NotFound('User not found')
            queryset = queryset.filter(pk=user.id)

        user_id = self.request.query_params.get('user_id', None)
        if user_id is not None:
            try:
                user = UserProfile.objects.get(
                    pk=user_id)
            except UserProfile.DoesNotExist:
                raise NotFound('User not found')

            queryset = queryset.filter(pk=user.pk)
        return queryset.order_by('last_name', 'first_name', 'email')


class CircleAffiliationSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()

    class Meta:
        model = CircleAffiliation
        fields = (
            'pk',
            'joined',
            'left',
            'user',
            'email',
            'circle',
            'created',
            'modified'
        )
        readonly_fields = ('created', 'modified')


class CircleAffiliationViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = CircleAffiliation.objects.all()
    serializer_class = CircleAffiliationSerializer


class CircleSerializer(serializers.ModelSerializer):
    circleaffiliation_set = CircleAffiliationSerializer(
        many=True, read_only=True)

    class Meta:
        model = Circle
        fields = (
            'pk',
            'name',
            'circleaffiliation_set',
            'read_only',
            'created_by',
            'created',
            'modified'
        )
        readonly_fields = ('created', 'modified')


class CircleSerializerList(serializers.ModelSerializer):
    circleaffiliation_set = CircleAffiliationSerializer(
        many=True, read_only=True)
    created_by = UserProfileSerializer()

    class Meta:
        model = Circle
        fields = (
            'pk',
            'name',
            'circleaffiliation_set',
            'created_by',
            'created',
            'modified'
        )
        readonly_fields = ('created', 'modified')


class CircleViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = Circle.objects.all()
    serializer_class = CircleSerializer

    def list(self, request):
        user = self.request.user.pk
        circles = Circle.objects.filter(active=True).filter(
            Q(created_by=user) | Q(circleaffiliation__user=user)).distinct().order_by('name')
        return Response(CircleSerializerList(instance=circles, many=True).data)

    def create(self, request):
        data = request.data.copy()
        users = data.pop('circleaffiliation_set')
        data['created_by'] = request.user.pk

        serialized = self.get_serializer(data=data, partial=True)
        serialized.is_valid(raise_exception=True)

        with transaction.atomic():
            affiliation = serialized.save()
            print affiliation
            circleaffiliation = CircleAffiliation.objects.create(
                user=request.user,
                email=request.user.email,
                circle=affiliation
            )
            for user in users:
                email = user['email']
                if email != '':
                    try:
                        user = UserProfile.objects.get(email=email)
                    except UserProfile.DoesNotExist:
                        circleaffiliation = CircleAffiliation.objects.create(
                            email=email,
                            circle=affiliation
                        )
                        #textsEmail(request.user, 'CREATE_GROUP', email, affiliation)
                    else:
                        circleaffiliation = CircleAffiliation.objects.create(
                            user=user,
                            email=user.email,
                            circle=affiliation
                        )
                        if request.user.pk != user.pk:
                            Notification.createGroupNotifications(
                                request.user, Notification.Type.CREATE_GROUP, user, affiliation)
                            send_mail(self, '[MMB] Nuovo gruppo ', 'Sei stato invitato a partecipare ad un nuovo gruppo. Accedi subito a www.mymedbook.it', user.email)

        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk):
        data = request.data.copy()
        data['created_by'] = request.user.pk
        emails = sorted([entry['email'] for entry in data.pop('circleaffiliation_set')])

        try:
            circle = Circle.objects.get(pk=pk)
        except Circle.DoesNotExist:
            raise ValidationError('Circle not found')

        serialized = self.get_serializer(
            instance=circle, data=data, partial=True)
        serialized.is_valid(raise_exception=True)

        with transaction.atomic():
            circle = serialized.save()
            affiliations = circle.circleaffiliation_set.all().order_by('email')
            aff_emails = [affiliation.email for affiliation in affiliations]
            for email in emails:
                if email not in aff_emails and email != '':
                    try:
                        user = UserProfile.objects.get(email=email)
                    except UserProfile.DoesNotExist:
                        user = None
                        #textsEmail(self, request.user, 'EDIT_GROUP', email, circle)
                    else:
                        if request.user.pk != user.pk:
                            send_mail(self, '[MMB] Modifica di un gruppo ',
                                    'E\' stato modificato un gruppo di cui fai parte. Accedi subito a www.mymedbook.it', user.email)
                    CircleAffiliation.objects.create(
                        circle=circle, user=user, email=email)
            for affiliation in affiliations:
                if affiliation is not None and affiliation.user_id and affiliation.user_id!=request.user.pk:
                    aff = UserProfile.objects.get(pk=affiliation.user_id)
                    Notification.createGroupNotifications(
                        request.user, Notification.Type.EDIT_GROUP, aff, circle)
                    if affiliation.email not in emails:
                        affiliation.delete()
                        send_mail(self, '[MMB] Eliminazione da un gruppo ',
                                    'Sei stato eliminato da un gruppo di cui facevi parte. Accedi subito a www.mymedbook.it', affiliation.email)

        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk):
        user = request.user.id
        circle_id = pk
        try:
            circle = Circle.objects.get(pk=circle_id, created_by=user)
        except Circle.DoesNotExist:
            raise ValidationError({'message': 'Invalid circle'})
        else:
            for affiliation in circle.circleaffiliation_set.all():
                if affiliation is not None:
                    try:
                        user_aff = UserProfile.objects.get(pk=affiliation.user_id)
                    except UserProfile.DoesNotExist:
                        send_mail(self, '[MMB] Eliminazione gruppo ','E\' stato eliminato un gruppo di cui fai parte. Accedi subito a www.mymedbook.it', user_aff.email)
                    else:
                        if request.user.pk != user_aff.pk:
                            Notification.createGroupNotifications(
                                request.user, Notification.Type.CREATE_GROUP, user_aff, circle)
                            send_mail(self, '[MMB] Eliminazione gruppo ',
                                    'E\' stato eliminato un gruppo di cui fai parte. Accedi subito a www.mymedbook.it', user_aff.email)
            circle.active=False
            circle.save()

        return Response({'message': 'ok'})


class CommentSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()

    class Meta:
        model = Comment
        fields = (
            'pk',
            'text',
            'post',
            'user',
            'created',
            'modified'
        )
        readonly_fields = ('created', 'modified')


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def create(self, request):
        data = request.data.copy()
        serializer = self.get_serializer(data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(user=request.user)
        post = comment.post
        for group in post.circle.all():
            notifications = Notification.createPostNotifications(
                request.user, Notification.Type.CREATE_POST, group, post, pk=post.pk)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        user = self.request.user
        queryset = Comment.objects.all()
        post = self.request.query_params.get('post')

        if post:
            queryset = queryset.filter(post=post, user=user).order_by('created')

        return queryset


class DocumentSerializer(serializers.ModelSerializer):
    document = serializers.FileField(use_url=False)

    class Meta:
        model = Document
        fields = (
            'pk',
            'document',
            'desc',
            'meta_info',
            'name',
            'dossier',
            'post',
            'created',
            'modified'
        )
        readonly_fields = ('created', 'modified')


class DocumentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def destroy(self, request, pk):
        user = request.user.id
        document_id = pk
        try:
            document = Document.objects.get(pk=document_id)
        except Document.DoesNotExist:
            raise ValidationError({'message': 'Invalid document'})
        else:
            document.delete()

        return Response({'message': 'ok'})

class PostSerializer(serializers.ModelSerializer):
    comment_set = CommentSerializer(many=True, required=False)
    document_set = DocumentSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = (
            'pk',
            'text',
            'user',
            'comment_set',
            'document_set',
            'circle',
            'created',
            'modified'
        )
        readonly_fields = ('created', 'modified')


class PostExpandedSerializer(PostSerializer):
    user = UserProfileMinimalSerializer()
    comment_set = CommentSerializer(many=True, required=False)
    document_set = DocumentSerializer(
        many=True, required=False, read_only=True)

class PostViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = Post.objects.all()
    serializer_class = PostExpandedSerializer
    pagination_class = StandardResultsSetPagination

    ''' def list(self, request):
        user = request.user
        circles = [
            aff.circle for aff in CircleAffiliation.objects.filter(user=user)]
        posts = Post.objects.filter(Q(user=user) | Q(
            circle__in=circles)).distinct().order_by('-created')

        return Response(PostExpandedSerializer(instance=posts, many=True).data)
    '''

    def get_queryset(self):
        user = self.request.user
        circles = [
            aff.circle for aff in CircleAffiliation.objects.filter(user=user)]
        posts = Post.objects.filter(Q(user=user) | Q(
            circle__in=circles)).distinct().order_by('-created')

        return posts

    def create(self, request):
        data = request.data.copy()
        data['user'] = request.user.pk
        serializer = PostSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save()
        # Notifica
        groups = post.circle.all()
        for group in groups:
            notifications = Notification.createPostNotifications(
                request.user, Notification.Type.CREATE_POST, group, post, pk=post.pk)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk):
        user = request.user.id
        post_id = pk
        try:
            post = Post.objects.get(pk=post_id, user=user)
        except Post.DoesNotExist:
            raise ValidationError({'message': 'Invalid Post'})
        else:
            post.delete()

        return Response({'message': 'ok'})


class TherapySimpleSerializer(serializers.ModelSerializer):
    #attachments = DocumentSerializer(many=True)
    #posologiestherapy_set = PosologiesTherapySerializer(many=True)

    class Meta:
        model = Therapy
        fields = (
            'pk',
            'name',
            'start_date',
            'end_date',
            'drug',
            #'treatment_plan',
            #'instructions',
            #'active',
            #'notification',
            #'lifesaver',
            #'doctor',
            #'attachments',
            #'posologiestherapy_set',
            #'user',
            #'created',
            #'modified'
        )
        #readonly_fields = ('created', 'modified')

class EventSimpleSerializer(serializers.ModelSerializer):
    #event_type = EventTypeSerializer()
    #dossier = DossierSerializer()
    #user = UserProfileMinimalSerializer()

    class Meta:
        model = Event
        fields = (
            'pk',
            'name',
            #'desc',
            'start_date',
            'end_date',
            #'notification',
            #'authority',
            #'address',
            #'user',
            'event_type',
            #'circle',
            #'dossier',
            #'created',
            #'modified'
        )
        #readonly_fields = ('created', 'modified')

class DossierSerializer(serializers.ModelSerializer):
    # circle = CircleSerializer(many=True, required=False, read_only=True)
    document_set = DocumentSerializer(
        many=True, required=False, read_only=True)
    event_set = EventSimpleSerializer(many=True, required=False)
    therapy_set = TherapySimpleSerializer(many=True, required=False)

    class Meta:
        model = Dossier
        fields = (
            'pk',
            'name',
            'meta_info',
            'user',
            'circle',
            'fiscal_code',
            'document_set',
            'therapy_set',
            'event_set',
            'created',
            'modified'
        )
        readonly_fields = ('created', 'modified')


class DossierViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = Dossier.objects.all()
    serializer_class = DossierSerializer

    def list(self, request):
        user = request.user
        circles = Circle.objects.filter(active=True).filter(
            Q(created_by=user) | Q(circleaffiliation__user=user)).distinct()
        dossiers = Dossier.objects.filter(
            Q(user=user) |
            Q(circle__in=circles)).distinct()
        return Response(DossierSerializer(instance=dossiers, many=True).data)

    def create(self, request):
        data = request.data.copy()
        circles_idx = data.pop('circle', None)

        data['user'] = request.user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        dossier = serializer.save()
        if circles_idx is not None:
            for circle in circles_idx:
                try:
                    circle_instance = Circle.objects.get(pk=circle)
                except Circle.DoesNotExist:
                    raise ValidationError({"message": "circle not found"})
                else:
                    dossier.circle.add(circle_instance)
                    for affiliation in circle_instance.circleaffiliation_set.all():
                        try:
                            user_aff = UserProfile.objects.get(
                                pk=affiliation.user_id)
                        except UserProfile.DoesNotExist:
                            send_mail(self, '[MMB] Nuovo dossier ', 'Sei stato invitato a partecipare ad un nuovo dossier. Accedi subito a www.mymedbook.it', user_aff.email)
                        else:
                            if request.user.pk != user_aff.pk:
                                Notification.createGroupNotifications(
                                    request.user, Notification.Type.CREATE_DOSSIER, user_aff, circle_instance)
                                send_mail(
                                    self, '[MMB] Nuovo dossier ', 'Sei stato invitato a partecipare ad un nuovo dossier. Accedi subito a www.mymedbook.it', user_aff.email)

        return Response(DossierSerializer(instance=dossier).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk):

        circles_idx = request.data.pop('circle')
        event_set =  request.data.pop('event_set')
        therapy_set = request.data.pop('therapy_set')
        document_set = request.data.pop('document_set')

        try:
            dossier = Dossier.objects.get(pk=pk)
        except Dossier.DoesNotExist:
            raise ValidationError('Dossier not found')

        with transaction.atomic():
            serialized = DossierSerializer(
                instance=dossier, data=request.data, partial=True)
            serialized.is_valid(raise_exception=True)
            dossier_instance = serialized.save()

        # prendo tutte le cerchie associate al dossier e le elimino
        for dossier_circle in dossier_instance.circle.all():
            dossier_circle = None

        # se non sto associando un dossie a nessuna cerchia elimino le
        # occorrenze che erano precedentemente salvate
        if not circles_idx:
            dossier_instance.circle = []
        else:
            dossier_instance.circle = []
            for circle in circles_idx:
                if circle:
                    try:
                        circle_instance = Circle.objects.get(pk=circle)
                    except Circle.DoesNotExist:
                        raise ValidationError({"message": "circle not found"})
                    else:
                        dossier_instance.circle.add(circle_instance)
                        dossier_instance.save()
                        for affiliation in circle_instance.circleaffiliation_set.all():
                            try:
                                user_aff = UserProfile.objects.get(
                                    pk=affiliation.user_id)
                            except UserProfile.DoesNotExist:
                                 send_mail(
                                        self, '[MMB] dossier modificato ', 'Hanno modificato un dossier condiviso con te. Accedi subito a www.mymedbook.it', affiliation.email)
                            else:
                                if request.user.pk != user_aff.pk:
                                    Notification.createGroupNotifications(
                                        request.user, Notification.Type.EDIT_DOSSIER, user_aff, circle_instance)
                                    send_mail(
                                        self, '[MMB] dossier modificato ', 'Hanno modificato un dossier condiviso con te. Accedi subito a www.mymedbook.it', user_aff.email)
        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk):
        print "delete"
        user = request.user.id
        dossier_id = pk
        try:
            dossier = Dossier.objects.get(pk=dossier_id)
        except Dossier.DoesNotExist:
            raise ValidationError({'message': 'Invalid circle'})
        else:
            for circle in dossier.circle.all():
                print circle.circleaffiliation_set.all()
                for affiliation in circle.circleaffiliation_set.all():
                    if affiliation is not None:
                        print affiliation
                        try:
                            user_aff = UserProfile.objects.get(
                                pk=affiliation.user_id)
                        except UserProfile.DoesNotExist:
                            send_mail(self, '[MMB] Dossier eliminato ', 'E\' stato eliminato un dossier condiviso con te. Accedi subito a www.mymedbook.it', affiliation.email)
                        else:
                            if request.user.pk != affiliation.user_id:
                                Notification.createGroupNotifications(
                                    request.user, Notification.Type.DELETED_DOSSIER, user_aff, circle)
                                send_mail(
                                    self, '[MMB] Dossier eliminato ', 'E\' stato eliminato un dossier condiviso con te. Accedi subito a www.mymedbook.it', affiliation.email)

            dossier.active=False
            dossier.save()

        return Response({'message': 'ok'})


class PosologiesTherapySerializer(serializers.ModelSerializer):

    class Meta:
        model = PosologiesTherapy
        fields = '__all__'


class TherapySerializer(serializers.ModelSerializer):
    attachments = DocumentSerializer(many=True)
    posologiestherapy_set = PosologiesTherapySerializer(many=True)

    class Meta:
        model = Therapy
        fields = (
            'pk',
            'name',
            'start_date',
            'end_date',
            'drug',
            'treatment_plan',
            'instructions',
            'active',
            'notification',
            'lifesaver',
            'doctor',
            'attachments',
            'posologiestherapy_set',
            'user',
            'created',
            'modified'
        )
        readonly_fields = ('created', 'modified')


class TherapyViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = Therapy.objects.all()
    serializer_class = TherapySerializer

    def list(self, request):
        user = request.user
        if self.request.query_params.get('user'):
            try:
                user = UserProfile.objects.get(
                    pk=self.request.query_params.get('user'))
            except UserProfile.DoesNotExist:
                raise NotFound('User not found')
        therapies = Therapy.objects.filter(user=user)
        return Response(TherapySerializer(instance=therapies, many=True).data)

    def create(self, request):
        user = request.user
        data = request.data.copy()
        data['user'] = user.pk
        posologies = data.pop('posologiestherapy_set', [])
        with transaction.atomic():
            serialized = TherapySerializer(data=data, partial=True)
            serialized.is_valid(raise_exception=True)
            therapy = serialized.save()
            if len(posologies) > 0:
                for posology in posologies:
                    if posology['posology'] != "" and posology['hour'] is not None:
                        posologySerialized = PosologiesTherapySerializer(
                            data=posology, partial=True)
                        posologySerialized.is_valid(raise_exception=True)
                        posologySerialized.save(therapy=therapy)

        return Response(serialized.data)

    def update(self, request, pk):
        data = request.data.copy()
        posologies = data.pop('posologiestherapy_set', [])
        attachments = data.pop('attachments', [])
        try:
            therapy = Therapy.objects.get(pk=pk)
        except Therapy.DoesNotExist:
            raise ValidationError('Therapy not found')

        with transaction.atomic():
            serialized = TherapySerializer(
                instance=therapy, data=data, partial=True)
            serialized.is_valid(raise_exception=True)
            therapy_instance = serialized.save()

            if len(posologies) > 0:
                PosologiesTherapy.objects.filter(therapy=therapy).delete()
                for posology in posologies:
                    if posology['posology'] != "" and posology['hour'] is not None:
                        posologySerialized = PosologiesTherapySerializer(
                            data=posology, partial=True)
                        posologySerialized.is_valid(raise_exception=True)
                        posologySerialized.save(therapy=therapy)
        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk):
        '''
            La delete e' intesa come modifica del campo left con la data odierna
        '''
        Therapy.objects.get(pk=pk).delete()

        return Response({'message': 'ok'})

    def get_queryset(self):
        user = self.request.user
        queryset = Therapy.objects.filter(user_id=user.pk)
        if self.request.query_params.get('user'):
            try:
                user = UserProfile.objects.get(
                    pk=self.request.query_params.get('user'))
            except UserProfile.DoesNotExist:
                raise NotFound('User not found')
            queryset = Therapy.objects.filter(user_id=user.pk)

        return queryset


class EventTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventType
        fields = (
            'pk',
            'name',
            'symbol',
            'created',
            'modified'
        )
        readonly_fields = ('created', 'modified')


class EventTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer

class EventSerializerForPostPut(serializers.ModelSerializer):
    event_type = EventTypeSerializer()
    dossier = DossierSerializer()

    class Meta:
        model = Event
        fields = (
            'pk',
            'name',
            'desc',
            'start_date',
            'end_date',
            'notification',
            'authority',
            'address',
            'user',
            'event_type',
            'circle',
            'dossier',
            'created',
            'modified'
        )
        readonly_fields = ('created', 'modified')

class EventSerializer(serializers.ModelSerializer):
    event_type = EventTypeSerializer()
    dossier = DossierSerializer()
    user = UserProfileMinimalSerializer()
    attachments = DocumentSerializer(
        many=True, required=False, read_only=True)

    class Meta:
        model = Event
        fields = (
            'pk',
            'name',
            'desc',
            'start_date',
            'end_date',
            'notification',
            'authority',
            'address',
            'user',
            'event_type',
            'circle',
            'dossier',
            'attachments',
            'created',
            'modified'
        )
        readonly_fields = ('created', 'modified')


class EventViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def create(self, request):
        data = request.data.copy()
        data['user'] = request.user.pk
        dossier_pk = data.pop('dossier', None)
        event_type_pk = data.pop('event_type', None)

        with transaction.atomic():
            serializer = EventSerializerForPostPut(data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            event = serializer.save()

            if event_type_pk:
                try:
                    event_type = EventType.objects.get(pk=event_type_pk)
                except EventType.DoesNotExist:
                    raise ValidationError('Event type not found')
                event.event_type = event_type
                event.save()
            if dossier_pk:
                try:
                    dossier = Dossier.objects.get(
                        pk=dossier_pk, user=request.user)
                except Dossier.DoesNotExist:
                    raise ValidationError('Dossier not found')
                event.dossier = dossier
                event.save()
            if event.circle.all().count() > 0 and event.notification:
                for circle in event.circle.all():
                    for affiliation in circle.circleaffiliation_set.all():
                        if affiliation is not None:
                            try:
                                user_aff = UserProfile.objects.get(
                                    pk=affiliation.user_id)
                            except UserProfile.DoesNotExist:
                                send_mail(self, '[MMB] Nuovo evento', 'E\' stato condiviso con te un nuovo evento. Accedi subito a www.mymedbook.it', affiliation.email)
                            else:
                                if request.user.pk != user_aff.pk:
                                    Notification.createGroupNotifications(
                                        request.user, Notification.Type.CREATE_EVENT, user_aff, circle)
                                    send_mail(
                                        self, '[MMB] Nuovo evento', 'E\' stato condiviso con te un nuovo evento. Accedi subito a www.mymedbook.it', affiliation.email)

        return Response(serializer.data)

    def update(self, request, pk):
        data = request.data.copy()
        user = request.user
        data['user']=user.pk

        event_type_pk = data.pop('event_type', None)
        dossier_pk = data.pop('dossier', None)
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            raise ValidationError('Event not found')

        with transaction.atomic():
            serializer = EventSerializerForPostPut(
                instance=event, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            event = serializer.save()

            if event_type_pk:
                try:
                    event_type = EventType.objects.get(pk=event_type_pk)
                except EventType.DoesNotExist:
                    raise ValidationError('Event type not found')
                event.event_type = event_type
                event.save()

            if dossier_pk:
                try:
                    dossier = Dossier.objects.get(
                        pk=dossier_pk, user=request.user)
                except Dossier.DoesNotExist:
                    raise ValidationError('Dossier not found')
                event.dossier = dossier
                event.save()

            if event.circle.all().count() > 0 and event.notification:
                for circle in event.circle.all():
                    for affiliation in circle.circleaffiliation_set.all():
                        if affiliation is not None:
                            try:
                                user_aff = UserProfile.objects.get(
                                    pk=affiliation.user_id)
                            except UserProfile.DoesNotExist:
                                send_mail(self, '[MMB] Evento modificato', 'E\' stato modificato un evento condiviso con te. Accedi subito a www.mymedbook.it', affiliation.email)
                            else:
                                if request.user.pk != user_aff.pk:
                                    Notification.createGroupNotifications(
                                        request.user, Notification.Type.EDIT_EVENT, user_aff, circle)
                                    send_mail(
                                        self, '[MMB] Evento modificato', 'E\' stato modificato un evento condiviso con te. Accedi subito a www.mymedbook.it', affiliation.email)

        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user
        queryset = Event.objects.filter(Q(user=user) | Q(circle__circleaffiliation__user=user)).distinct().order_by('pk')

        return queryset

def destroy(self, request, pk):
        user = request.user.id
        event_id = pk
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            raise ValidationError({'message': 'Invalid event'})
        else:
            if event.circle.all().count() > 0 and event.notification:
                for circle in event.circle.all():
                    for affiliation in circle.circleaffiliation_set.all():
                        if affiliation is not None:
                            try:
                                user_aff = UserProfile.objects.get(
                                    pk=affiliation.user_id)
                            except UserProfile.DoesNotExist:
                                send_mail(self, '[MMB] Evento elimianto ', 'E\' stato eliminato un evento condiviso con te. Accedi subito a www.mymedbook.it', affiliation.email)
                            else:
                                if request.user.pk != affiliation.user_id:
                                    Notification.createGroupNotifications(
                                        request.user, Notification.Type.DELETED_EVENT, user_aff, circle)
                                    send_mail(
                                        self, '[MMB] Evento elimianto ', 'E\' stato eliminato un evento condiviso con te. Accedi subito a www.mymedbook.it', affiliation.email)

        event.delete()

class SensorSerializer(serializers.ModelSerializer):
    structure = StructureSerializer(read_only=True)

    class Meta:
        model = Sensor
        fields = (
            'pk',
            'caption',
            'identifier',
            'structure',
            'created',
            'modified'
        )


class SensorViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer


class AlarmSerializer(serializers.ModelSerializer):
    sensor = SensorSerializer(read_only=True)
    caller = UserProfileMinimalSerializer()
    handler = UserProfileMinimalSerializer()

    class Meta:
        model = Alarm
        fields = (
            'pk',
            'message',
            'date',
            'handled',
            'caller',
            'handler',
            'sensor',
            'created',
            'modified'
        )


class AlarmViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = Alarm.objects.all()
    serializer_class = AlarmSerializer

    def get_queryset(self):
        user = self.request.user
        structure_id = self.request.query_params.get('structure_id')
        handled = self.request.query_params.get('handled')
        try:
            structure = Structure.objects.get(pk=structure_id)
        except Structure.DoesNotExist:
            raise ValidationError('Structre not found')

        timestamp = datetime.now() - timedelta(days=1)

        alarms = Alarm.objects.filter(
            sensor__structure=structure, date__gte=timestamp)
        if handled:
            alarms = alarms.filter(handled=False)

        return alarms

# conversation e message


class ConversationExpandedSerializer(AllFieldsSerializer):
    mhash = serializers.CharField(write_only=True)
    members = UserProfileSerializer(many=True)

    class Meta:
        model = Conversation
        fields = '__all__'


class ConversationSerializer(AllFieldsSerializer):
    mhash = serializers.CharField(write_only=True)

    class Meta:
        model = Conversation
        fields = '__all__'


class ConversationWithMessagesSerializer(ConversationSerializer):
    members = UserProfileSerializer(read_only=True, many=True)
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = '__all__'

    def get_messages(self, conversation):
        messages = Message.objects.filter(conversation=conversation)
        first = MessageSerializer(instance=messages.first()).data
        last = MessageSerializer(instance=messages.last()).data
        return {'first': first, 'last': last}

# TODO: deve diventare APIView


class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        userConversations = UsersConversations.objects.filter(
            user_id=self.request.user).values('conversation_id')
        return Conversation.objects.filter(pk__in=userConversations)

    def create(self, request):
        members1 = request.data.pop('members', [])
        message_data = request.data.pop('message', [])
        members = set(UserProfile.objects.filter(
            email__in=[members1, request.user.email]))
        # se esiste gia una conversazione creata dall'utente loggato che ha i
        # soliti partecipanti
        print members
        mhash = Conversation.make_hash(members)

        try:
            conv = Conversation.objects.get(mhash=mhash)
        except Conversation.DoesNotExist:
            pass
        else:
            if conv.members.all().count() == 2:
                userConversations = UsersConversations.objects.filter(
                    conversation=conv, active=False)
                for userConv in userConversations:
                    userConv.active = True
                    userConv.save()
                message = Message.objects.create(
                    user=request.user,
                    text=message_data['text'],
                    conversation=conv
                )
                notifications = Notification.createConversationNotifications(request.user, conv, message)
            return Response(ConversationExpandedSerializer(instance=conv).data)
        data = request.data.copy()
        data['mhash'] = mhash
        members1_instance= UserProfile.objects.get(email=members1)
        data['title'] = '%s - %s' % (members1_instance.first_name, request.user.first_name)

        serialized = ConversationSerializer(data=data, partial=True)
        serialized.is_valid(raise_exception=True)

        with transaction.atomic():
            conversation = serialized.save(
                created_by=request.user)
            message = Message.objects.create(
                user=request.user,
                text=message_data['text'],
                conversation=conversation
            )
            message.save()
            for member in members:
                UsersConversations.objects.create(
                    user=member, conversation=conversation)
            notifications = Notification.createConversationNotifications(
                request.user, conversation, message)


        return Response(ConversationExpandedSerializer(instance=conversation).data)


###MESSAGE###
class MessageSerializerExpanded(AllFieldsSerializer):
    created = serializers.SerializerMethodField()
    user = UserProfileMinimalSerializer()

    class Meta:
        model = Message
        exclude = ('modified', )

    def get_created(self, message):
        return message.get_created_ts()


class MessageSerializer(AllFieldsSerializer):
    created = serializers.SerializerMethodField()

    class Meta:
        model = Message
        exclude = ('modified', )

    def get_created(self, message):
        return message.get_created_ts()


class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = Message.objects.all()
    serializer_class = MessageSerializerExpanded

    def create(self, request):
        try:
            conversation = Conversation.objects.get(
                pk=request.data.get('conversation'))
        except Conversation.DoesNotExist:
            raise NotFound('Conversation not found')

        data = request.data.copy()
        data['user'] = request.user.pk
        serialized = MessageSerializer(data=data)
        serialized.is_valid(raise_exception=True)

        with transaction.atomic():
            message = serialized.save(
                user=request.user, conversation=conversation)
            notifications = Notification.createConversationNotifications(
                request.user, conversation, message)

        Notification.process(notifications)

        return Response(serialized.data)

    @staticmethod
    def date_from_timestamp(value, offset):
        # datetime.fromtimestamp
        try:
            return datetime.utcfromtimestamp(float(value) + offset).replace(tzinfo=pytz.utc)
        except (TypeError, ValueError):
            raise ValidationError('Invalid timestamp specified %s' % value)

    def get_queryset(self):
        query_params = self.request.query_params

        try:
            conversation = Conversation.objects.get(
                pk=query_params.get('conv_id'))
            conversation.members.get(pk=self.request.user.id)
        except (Conversation.DoesNotExist, UserProfile.DoesNotExist):
            raise ValidationError('Invalid conversation')

        queryset = Message.objects.filter(conversation=conversation)

        from_ts = query_params.get('from_ts', None)
        to_ts = query_params.get('to_ts', None)

        if from_ts:
            queryset = queryset.filter(
                created__gte=self.date_from_timestamp(from_ts, -1))

        if to_ts:
            queryset = queryset.filter(
                created__lte=self.date_from_timestamp(to_ts, 1))

        if query_params.get('limit'):
            limit = int(query_params.get('limit'))
            queryset = queryset.order_by('-created')[:limit]
        else:
            queryset = queryset.order_by('-created')

        return queryset



### SERIALIZER FOR COC ###
class MymedtagStructureCOC(serializers.ModelSerializer):
    product_type = ProductTypeSerializer()
    structure_affiliation = StructureAffiliationSerializer()

    class Meta:
        model = MyMedTag
        fields = (
            'pk',
            'code',
            'product_type',
            'structure_affiliation',
            'active',
            'created',
            'modified'
        )
        readonly_fields = ('created', 'modified')

class SerialCOCSerializer(AllFieldsSerializer):

    class Meta:
        model = SerialCOC
        exclude = ('modified', )


class SerialCOCViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = SerialCOC.objects.all()
    serializer_class = SerialCOCSerializer

class ActionCOCSerializer(AllFieldsSerializer):
    class Meta:
        model = ActionCOC
        exclude = ('modified', )

class ActionCOCViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = ActionCOC.objects.all()
    serializer_class = ActionCOCSerializer

class StructureAffiliationSerializerCOC(serializers.ModelSerializer):
    user = UserProfileMinimalSerializer()

    class Meta:
        model = StructureAffiliation
        fields = (
            'pk',
            'joined',
            'left',
            'user',
            'structure',
            'mymedtag_set',
            'created',
            'modified'
        )
        readonly_fields = ('created', 'modified')

class AssistanceRequestSerializer(AllFieldsSerializer):
    affiliation = StructureAffiliationSerializerCOC()
    handler = UserProfileMinimalSerializer()

    class Meta:
        model = AssistanceRequest
        exclude = ('modified', )


class AssistanceRequestViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = AssistanceRequest.objects.all()
    serializer_class = AssistanceRequestSerializer
