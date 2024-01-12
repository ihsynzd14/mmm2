from django.db import models
from django.conf import settings
from django.utils.text import Truncator
from django.contrib.postgres.fields import JSONField, ArrayField
from django.contrib.postgres.fields import ArrayField
from django.core.mail import EmailMultiAlternatives

from model_utils.fields import AutoCreatedField, AutoLastModifiedField

from backend.models import UserProfile, UsersConversations
from pyfcm import FCMNotification
#
# fcm_service = FCMNotification(api_key=settings.FCM_API_KEY)

def send_mail(subject, context, to_email):
    print 'SEND_MAIL'
    subject = subject
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    body = context

    email_message = EmailMultiAlternatives(subject, body, None, [to_email])
    email_message.send()

class Device(models.Model):
    uuid = models.CharField(max_length=255, primary_key=True)
    first_registration = AutoCreatedField('first_registration')
    last_registration = AutoLastModifiedField('last_registration')
    token = models.TextField(blank=True)
    user = models.ForeignKey(UserProfile, null=True, blank=True)
    app_id = models.CharField(max_length=255, blank=True, null=True)
    app_version = models.CharField(max_length=32, blank=True, null=True)
    os_type = models.CharField(max_length=32, blank=True, null=True)
    os_version = models.CharField(max_length=32, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    locale = models.CharField(max_length=32, blank=True, null=True)


class Notification(models.Model):
    created = AutoCreatedField('created')
    sent = models.DateTimeField(blank=True, null=True)
    #device = models.ForeignKey(Device)
    title = models.CharField(max_length=255)
    tag = models.CharField(max_length=64, blank=True, null=True)
    body = models.TextField(blank=True)
    read = models.BooleanField(default=False)
    title_loc_key = models.CharField(max_length=64, blank=True, null=True)
    body_loc_key = models.CharField(max_length=64, blank=True, null=True)
    body_loc_arg = ArrayField(models.CharField(max_length=64, blank=True, null=True))
    tokens = ArrayField(models.TextField(), default=list)
    data_message = JSONField(default=dict)
    user = models.ForeignKey(UserProfile)

    class Type(object):
        CREATE_GROUP = {
            'tag': 'group_created',
            'type': 'group_created',
            'title': u'{group.name}',
            'body': u'{user.first_name} {user.last_name} ha creato un gruppo'
        }
        EDIT_GROUP = {
            'tag': 'group_edited',
            'type': 'group_edited',
            'title': u'{group.name}',
            'body': u'{user.first_name} {user.last_name} ha modificato un gruppo'
        }
        DELETED_GROUP = {
            'tag': 'group_deleted',
            'type': 'group_deleted',
            'title': u'{group.name}',
            'body': u'{user.first_name} {user.last_name} ha eliminato un gruppo'
        }
        CREATE_DOSSIER= {
            'tag': 'dossier_created',
            'type': 'dossier_created',
            'title': u'{group.name}',
            'body': u'{user.first_name} {user.last_name} ha creato un dossier'
        }
        EDIT_DOSSIER = {
            'tag': 'dossier_edited',
            'type': 'dossier_edited',
            'title': u'{group.name}',
            'body': u'{user.first_name} {user.last_name} ha modificato un dossier'
        }
        DELETED_DOSSIER = {
            'tag': 'dossier_deleted',
            'type': 'dossier_deleted',
            'title': u'{group.name}',
            'body': u'{user.first_name} {user.last_name} ha eliminato un dossier'
        }
        CREATE_EVENT= {
            'tag': 'event_created',
            'type': 'event_created',
            'title': u'{group.name}',
            'body': u'{user.first_name} {user.last_name} ha creato un evento'
        }
        EDIT_EVENT = {
            'tag': 'event_edited',
            'type': 'event_edited',
            'title': u'{group.name}',
            'body': u'{user.first_name} {user.last_name} ha modificato un evento'
        }
        DELETED_EVENT = {
            'tag': 'event_deleted',
            'type': 'event_deleted',
            'title': u'{group.name}',
            'body': u'{user.first_name} {user.last_name} ha eliminato un evento'
        }
        CREATE_POST = {
            'tag': 'post_created',
            'type': 'post_created',
            'title': u'{post.text}',
            'body': u'{user.first_name} {user.last_name} ha mandato un messaggio'
        }
        CONVERSATION = {
            'tag': 'message_{conversation.pk}',
            'type': 'message',
            'title': 'Nuovo messaggio',
            'body': u'{user.first_name} {user.last_name} ti ha inviato un messaggio'
        }

    @staticmethod
    def createPostNotifications(user, notification_type, group=None, post=None, **kwargs):
        notifications = []
        #for device in Device.objects.filter(user=friend, token__isnull=False):
        if post is not None:
            text = notification_type['title'].format(post=post)

        for affiliation in group.circleaffiliation_set.all():
            try:
                to_user = UserProfile.objects.get(pk=affiliation.user_id)
            except UserProfile.DoesNotExist:
                pass
            else:
                data_message = {
                    'from_user': user.id,
                    'to_user': affiliation.user_id,
                    'type': notification_type['type'],
                    'group': group.pk
                }

                data_message.update(kwargs)

                #tokens = [dev['token'] for dev in Device.objects.filter(user=friend, token__isnull=False).values('token')]
                tokens = {}
                notifications.append(Notification.objects.create(
                    #device=device,
                    user=to_user,
                    #tokens=tokens,
                    title=text,
                    title_loc_key=notification_type['tag'],
                    body_loc_key="%s_body" % notification_type['type'],
                    body_loc_arg=[user.first_name, user.last_name],
                    body=notification_type['body'].format(user=user),
                    data_message=data_message,
                    tag=notification_type['tag']))
            send_mail('[MMB] Messaggio in bacheca ',
                      'Hai un nuovo messaggio in bacheca. Accedi subito a www.mymedbook.it', affiliation.email)

        return notifications

    @staticmethod
    def createGroupNotifications(user, notification_type, affiliation=None, group=None):
        notifications = []
        #for device in Device.objects.filter(user=friend, token__isnull=False):
        text = notification_type['title'].format(group=group)
        data_message = {
            'from_user': user.id,
            'to_user': affiliation.pk,
            'type': notification_type['type'],
            'group': group.pk
        }

        #data_message.update(kwargs)
        #tokens = [dev['token'] for dev in Device.objects.filter(user=friend, token__isnull=False).values('token')]
        tokens = {}
        notifications.append(Notification.objects.create(
            #device=device,
            user=affiliation,
            #tokens=tokens,
            title=text,
            title_loc_key=notification_type['tag'],
            body_loc_key="%s_body" % notification_type['type'],
            body_loc_arg=[user.first_name, user.last_name],
            body=notification_type['body'].format(user=user),
            data_message=data_message,
            tag=notification_type['tag']))

        return notifications


    @staticmethod
    def createConversationNotifications(user, conversation, message, **kwargs):
        notification_type = Notification.Type.CONVERSATION
        notifications = []
        for member in conversation.members.exclude(pk=user.pk):
            if UsersConversations.objects.filter(conversation=conversation, user=member, active=True):
                #for device in Device.objects.filter(user=member, token__isnull=False):
                body = notification_type['body'].format(user=user)

                #body = Truncator(message.text).chars(100)

                data_message = {
                    'pk': message.pk,
                    'created': '%d' % message.get_created_ts(),
                    'pk_conv': conversation.pk,
                    'from_user': user.id,
                    'to_user': member.pk,
                    'type': notification_type['type']
                }
                data_message.update(kwargs)
                tokens = [dev['token'] for dev in Device.objects.filter(user=member, token__isnull=False).values('token')]
                notifications.append(Notification.objects.create(
                    #device=device,
                    user=member,
                    tokens=tokens,
                    title=message.text,
                    title_loc_key=notification_type['tag'],
                    body_loc_key="%s_body" % notification_type['type'],
                    body_loc_arg=[user.first_name, user.last_name],
                    body=body,
                    data_message=data_message,
                    tag=notification_type['tag'].format(conversation=conversation)))
                send_mail('[MMB] Nuovo messaggio ',
                  'Hai ricevuto un nuovo messaggio. Accedi subito a www.mymedbook.it', member.email)

        return notifications

    @staticmethod
    def process(notifications):
        pass
        '''for notification in notifications:
            if len(notification.tokens)<=0:
                return
            result = fcm_service.notify_multiple_devices(
                #registration_id=notification.device.token,
                registration_ids=notification.tokens,
                message_title=notification.title,
                message_body=notification.body,
                data_message=notification.data_message,
                tag=notification.tag)'''
