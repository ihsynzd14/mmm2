from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save

from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, AbstractUser
from django.contrib.postgres.fields import JSONField

from django.conf import settings
from django.dispatch import receiver

from model_utils.fields import AutoCreatedField, AutoLastModifiedField

from django.contrib.auth.models import Group

import os
import time
import hashlib

class TimeStampedModel(models.Model):
    created = AutoCreatedField('created')
    modified = AutoLastModifiedField('modified')

    class Meta:
        abstract = True

    def get_created_ts(self):
        return time.mktime(self.created.timetuple())


class Structure(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    max_members = models.IntegerField(null=True, blank=True)
    max_affiliates = models.IntegerField(null=True, blank=True)
    label = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    mobile_number = models.CharField(max_length=255, null=True, blank=True)
    code_type = models.CharField(max_length=255, null=True, blank=True)
    sostag_enabled = models.BooleanField(default=False)
    

    def __unicode__(self):
        return self.name


class AttributeGroup(TimeStampedModel):
    name = models.CharField(max_length=255)
    sorting = models.IntegerField(null=True, blank=True)
    structure = models.ForeignKey('Structure')

    def __unicode__(self):
        return self.name


class Enum(TimeStampedModel):
    value = models.CharField(max_length=255)
    attribute = models.ForeignKey('Attribute')

    def __unicode__(self):
        return self.value


class Attribute(TimeStampedModel):
    class Meta:
        ordering = ['group','sorting','id']

    DATATYPES = (
        ('text', 'Text'),
        ('boolean', 'Boolean'),
        ('number', 'Number'),
        ('year_with_checkbox', 'Year with Checkbox'),
        ('year_with_text', 'Year with Text'),
        ('label', 'Label'),
        ('enum', 'Choices'))
    name = models.CharField(max_length=255)#, unique=True)
    datatype = models.CharField(max_length=255, choices=DATATYPES)
    forced_lifesaver = models.BooleanField(default=False)
    sorting = models.IntegerField(null=True, blank=True)
    group = models.ForeignKey('AttributeGroup')

    def __unicode__(self):
        return self.name


class AttributeValueManager(models.Manager):

    @staticmethod
    def cast(d, datatype, value, other=None):
        if datatype == 'text':
            d['text_value'] = value
        elif datatype == 'boolean':
            d['boolean_value'] = value
        elif datatype in ('number','year_with_checkbox','year_with_text'):
            try:
                d['number_value'] = float(value)
            except:
                d['number_value'] = 0
        if datatype == 'year_with_text':
            d['text_value'] = other
        return d

    def attribute_value(self, func, **d):
        datatype = d['attribute'].datatype
        value = d.pop('value')
        other = d.pop('other', None)

        if datatype != 'enum':
            return func(**self.cast(d, datatype, value, other))

        if not value:
            return []

        results = []
        for enum in Enum.objects.filter(pk__in=value):
            d['enum'] = enum
            results.append(func(**d))
        return results

    def create_attribute_value(self, **d):
        return self.attribute_value(self.create, **d)

    def update_attribute_value(self, *args, **kwargs):
        instance = kwargs.pop('instance')
        func = self.model.objects.filter(pk=instance.pk).update
        return self.attribute_value(func, **kwargs)


class AttributeValue(TimeStampedModel):
    text_value = models.CharField(max_length=255, null=True, blank=True)
    boolean_value = models.BooleanField(default=False)
    number_value = models.FloatField(null=True, blank=True)
    date_value = models.CharField(max_length=255, null=True, blank=True)
    lifesaver = models.BooleanField(default=False)
    attribute = models.ForeignKey('Attribute')
    enum = models.ForeignKey(
        'Enum', blank=True, null=True)
    user = models.ForeignKey('UserProfile', null=True)

    objects = AttributeValueManager()

    class Meta:
        unique_together = ('user', 'attribute', 'enum')

    def __unicode__(self):
        try:
            return unicode(self.value) or u''
        except:
            return None

    @property
    def value(self):
        datatype = self.attribute.datatype
        if datatype == 'text':
            return self.text_value
        elif datatype == 'boolean':
            return self.boolean_value
        elif datatype == 'number':
            return self.number_value
        elif datatype == 'enum':
            return self.enum.value
        elif datatype in( 'year_with_checkbox','year_with_text'):
            if self.number_value is not None:
                return int(self.number_value)
            else:
                return None

        raise Exception('Invalid datatype ' + datatype)

    @property
    def other(self):
        datatype = self.attribute.datatype
        if datatype == 'year_with_text':
            return self.text_value
        else:
            return None

    @property
    def datatype(self):
        return self.attribute.datatype

    @property
    def name(self):
        return self.attribute.name

    @staticmethod
    def user_attributes(func, user, attributes, instance=None):
        #for attribute_value in attributes:
        try:
            attribute = Attribute.objects.get(pk=attributes['attribute'].pk)
        except Attribute.DoesNotExist:
            raise ValueError('Attibute does not exist')

        yield func(value=attributes.get('value'),
                    user=user,
                    other=attributes.get('other'),
                    attribute=attributes['attribute'],
                    lifesaver=attributes.get('lifesaver', False),
                    instance=instance)

    @staticmethod
    def create_user_attributes(user, attributes):
        func = AttributeValue.objects.create_attribute_value
        return list(AttributeValue.user_attributes(func, user, attributes))

    def update_user_attributes(self, user, attributes):
        func = AttributeValue.objects.update_attribute_value
        return list(AttributeValue.user_attributes(func, user, attributes, instance=self))


class UserProfile(AbstractUser):
    objects = UserManager()

    birthday = models.DateField(null=True, blank=True)
    fiscal_code = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    town = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    sex = models.CharField(max_length=255, null=True, blank=True)
    cap = models.IntegerField(null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    plaintext_password = models.CharField(
        max_length=255, null=True, editable=False)
    avatar = models.ImageField(blank=True)
    active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now_add=True, editable=False)
    lifesaver = models.ForeignKey('AttributeValue', null=True, blank=True, on_delete=models.SET_NULL)
    public_lifesaver = models.BooleanField(default=False)
    registered_by = models.ForeignKey(
        'UserProfile', related_name="+", null=True, blank=True)

    @property
    def bmi(self):
        if self.height and self.weight:
            return '%.2f' % (self.weight / pow(self.height / 100.0, 2))
        return '-'

    def __unicode__(self):
        return self.email

class Circle(TimeStampedModel):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey('UserProfile')
    read_only = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name


class Affiliation(TimeStampedModel):
    joined = models.DateField(auto_now_add=True)
    left = models.DateField(null=True, blank=True)
    user = models.ForeignKey('UserProfile')

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.user.email

class CircleAffiliation(Affiliation):
    circle = models.ForeignKey('Circle')
    user = models.ForeignKey('UserProfile', null=True, blank=True)
    email = models.EmailField()

    class Meta(Affiliation.Meta):
        unique_together = ('circle', 'email')

    def __unicode__(self):
        return self.email

    @property
    def name(self):
        return self.circle.name

    @property
    def created_by(self):
        return self.circle.created_by


class StructureAffiliation(Affiliation):
    structure = models.ForeignKey('Structure',)

    class Meta:
        unique_together = ('user', 'structure')

class StructureMembership(Affiliation):
    structure = models.ForeignKey('Structure',)

    class Meta:
        unique_together = ('user', 'structure')


class Post(TimeStampedModel):
    text = models.TextField()
    user = models.ForeignKey('UserProfile')
    circle = models.ManyToManyField('Circle')


class Comment(TimeStampedModel):
    text = models.TextField()
    post = models.ForeignKey('Post')
    user = models.ForeignKey('UserProfile')


class Dossier(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    meta_info = models.TextField(null=True, blank=True)
    user = models.ForeignKey('UserProfile',)
    fiscal_code = models.CharField(max_length=255, null=True, blank=True)
    circle = models.ManyToManyField('Circle', blank=True)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name


class Document(TimeStampedModel):
    document = models.FileField(upload_to='documents/')
    desc = models.TextField(null=True, blank=True)
    meta_info = models.TextField(null=True, blank=True)
    dossier = models.ForeignKey('Dossier', null=True, blank=True)
    post = models.ForeignKey('Post', null=True, blank=True)

    @property
    def name(self):
        return os.path.basename(self.document.name)

class Therapy(TimeStampedModel):
    name = models.CharField(max_length=255)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    drug = models.TextField(null=True, blank=True)
    treatment_plan = models.TextField(null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    notification = models.BooleanField(default=False)
    lifesaver = models.BooleanField(default=False)
    doctor = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey('UserProfile')
    circle = models.ManyToManyField('Circle')
    attachments = models.ManyToManyField('Document')
    dossier = models.ForeignKey('Dossier', null=True, blank=True)

class PosologiesTherapy(TimeStampedModel):
    posology = models.TextField()
    hour = models.TimeField()
    therapy = models.ForeignKey('Therapy', null=True, blank=True)

class EventType(TimeStampedModel):
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=255, null=True)

    def __unicode__(self):
        return self.name


class Event(TimeStampedModel):
    name = models.CharField(max_length=255)
    desc = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    notification = models.BooleanField(default=False)
    authority = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey('UserProfile')
    event_type = models.ForeignKey('EventType', null=True, blank=True)
    circle = models.ManyToManyField('Circle', blank=True)
    attachments = models.ManyToManyField('Document')
    dossier = models.ForeignKey('Dossier', null=True, blank=True)

class Sensor(TimeStampedModel):
    caption = models.TextField(blank=True)
    identifier = models.CharField(max_length=255, blank=True)
    structure = models.ForeignKey('Structure')

    def __unicode__(self):
        return self.caption


class Alarm(TimeStampedModel):
    message = models.TextField(blank=True)
    date = models.DateTimeField(blank=True)
    handled = models.BooleanField(default=False)
    caller = models.ForeignKey('UserProfile', related_name="caller")
    handler = models.ForeignKey('UserProfile', related_name="handler",null=True, blank=True)
    sensor = models.ForeignKey('Sensor')

class Serial(TimeStampedModel):
    MMTCode = models.CharField(max_length=255)
    serial_tag = models.CharField(max_length=255)

class InterestedTag(TimeStampedModel):
    email = models.CharField(max_length=255)
    tag = models.CharField(max_length=255)

class ProductType(TimeStampedModel):
    name = models.CharField(max_length=255)
    cover = models.ImageField(blank=True)

    def __unicode__(self):
        return self.name

class MyMedTag(TimeStampedModel):
    code = models.CharField(max_length=255)
    structure_affiliation = models.ForeignKey('StructureAffiliation', null=True, blank=True)
    structure_membership = models.ForeignKey('StructureMembership', null=True, blank=True)
    product_type = models.ForeignKey('ProductType', null=True, blank=True)
    active = models.BooleanField(default=True)

class Message(TimeStampedModel):
    user = models.ForeignKey(UserProfile)
    text = models.TextField()
    conversation = models.ForeignKey('Conversation')
    readers = models.ManyToManyField('UserProfile', related_name='readers', blank=True)

class UsersConversations(TimeStampedModel):
    user = models.ForeignKey(UserProfile)
    conversation = models.ForeignKey('Conversation')
    active = models.BooleanField(default=True)

class ConversationManager(models.Manager):
    def create(self, *args, **kwargs):
        return super(ConversationManager, self).create(*args, **kwargs)

class Conversation(TimeStampedModel):
    objects = ConversationManager()

    mhash = models.CharField(max_length=64, unique=True)
    created_by = models.ForeignKey(UserProfile, null=True, blank=True,  related_name='+')
    title = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    members = models.ManyToManyField(UserProfile, through='UsersConversations')

    def save(self, *args, **kwargs):
        return super(Conversation, self).save(*args, **kwargs)
        members = set(UserProfile.objects.filter(pk__in=kwargs.pop('members', [])))
        for member in members:
            # non puoi aprire una conversazione con un utente che ti ha bloccato
            try:
                member.blocked_users.get(pk=validated_data.created_by.id)
            except UserProfile.DoesNotExist:
                pass
            else:
                raise ValueError('Unable to create the conversation')

        members.add(kwargs['created_by'])

        if len(members) < 2:
            raise ValueError('Conversations must have a minimum of two members')

        # se esiste gia una conversazione creata dall'utente loggato che ha i
        # soliti partecipanti
        mhash = Conversation.make_hash(members)

        try:
            conversation = Conversation.objects.get(mhash=mhash)
        except Conversation.DoesNotExist:
            pass
        else:
            # controllare se gli utenti della conversazione sono disattivati nel caso riattivarli
            if conversation.members.all().count() == 2:
                for userconv in UsersConversations.objects.filter(conversation=conv, active=False):
                    userconv.active = True
                    userconv.save()
            return conversation

        with transaction.atomic():
            conversation.mhash = mhash
            conversation = super(Conversation, self).save(*args, **kwargs)

            for member in members:
                UsersConversations.objects.create(user=member, conversation=conversation)

        return conversation

    @staticmethod
    def make_hash(members, **kwargs):
        m = hashlib.sha256()
        members_pks = ','.join(sorted([str(member.pk) for member in members ]))
        m.update(members_pks)
        m.update('--')
        for key in sorted(kwargs.keys()):
            m.update('|'.join([key, str(kwargs[key])]))
        m.update('--')
        return m.hexdigest()

## Models for COC ##
class SerialCOC(TimeStampedModel):
    duration = models.IntegerField(default=0)
    serial = models.CharField(max_length=255,)
    valid = models.BooleanField(default=False)
    start_date_validation = models.DateField(null=True, blank=True)
    affiliation = models.ForeignKey(StructureAffiliation, null=True, blank=True)
    structure = models.ForeignKey(Structure, null=True, blank=True)

class ActionCOC(TimeStampedModel):
    ACTIONTYPES = (
        ('sms', 'Sms'),
        ('call', 'Call'),
        ('email', 'Email'),
        ('circle', 'Gruppi'))
    name = models.CharField(max_length=255)
    label = models.CharField(max_length=255, null=True, blank=True)
    action_type = models.CharField(max_length=255, choices=ACTIONTYPES)
    circle = models.ForeignKey(Circle, null=True, blank=True)
    affiliation = models.ManyToManyField(StructureAffiliation)
    value = models.CharField(max_length=255, null=True, blank=True)

class AssistanceRequest(TimeStampedModel):
    date = models.DateTimeField(blank=True)
    handled = models.BooleanField(default=False)
    affiliation = models.ForeignKey(StructureAffiliation, null=True, blank=True)
    latlng = models.PointField(null=True, blank=True)
    structure = models.ForeignKey(Structure)
    handler = models.ForeignKey(UserProfile, related_name="assistancehandler",null=True, blank=True)
