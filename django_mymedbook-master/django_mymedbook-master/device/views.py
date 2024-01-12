from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import ValidationError, NotFound

from django.conf import settings

from pyfcm import FCMNotification
#fcm_service = FCMNotification(api_key=settings.FCM_API_KEY)

from models import Device, Notification
from serializers import *


class RegisterDevice(APIView):
    def post(self, request, uuid):
        device, created = Device.objects.update_or_create(uuid=uuid, defaults=request.data)
        if request.user.is_authenticated():
            device.user = request.user
            device.save()
        return Response({'message':'ok'})

class BindDevice(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, uuid):
        try:
            device = Device.objects.get(uuid=uuid)
        except Device.DoesNotExist:
            raise NotFound('Device not found')

        device.user = request.user
        device.save()

        return Response({'message': 'ok'})

class UnbindDevice(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, uuid):
        try:
            device = Device.objects.get(uuid=uuid)
        except Device.DoesNotExist:
            raise ValidationError('Device not found')

        device.user = None
        device.save()

        return Response({'message': 'ok'})

class SendNotification(APIView):
    permission_classes = (IsAdminUser, )

    def post(self, request):
        devices = Device.objects.filter(token__isnull=False, user__pk=request.data.pop('user'))
        if not devices:
            raise ValidationError('No devices associated to user')

        title = request.data.pop('title')
        body = request.data.pop('body')
        ids = [device.token for device in devices]
        result = fcm_service.notify_multiple_devices(
            registration_ids=ids,
            message_title=title,
            message_body=body
        )

        return Response(result)

class CheckNotificationAsRead(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        #devices = Device.objects.filter(token__isnull=False, user=request.user)
        #if not devices:
        #    raise ValidationError('No devices associated to user')
        #notifications = Notification.objects.filter(device__in=devices)
        notifications = Notification.objects.filter(user=request.user, read=False)
        with transaction.atomic():
            for notification in notifications:
                serialized = NotificationSerializer(instance=notification, data={'read':True}, partial=True)
                serialized.is_valid(raise_exception=True)
                serialized.save()
        return Response({'message':'ok'})

class CheckNotificationFrontendAsRead(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        item_idx = request.data.pop('item_idx')
        item_type = request.data.pop('item_type')
        if item_type=="posts":
            if len(item_idx)>0:
                notifications = Notification.objects.filter(user=request.user, tag__contains='post', data_message__pk__in=item_idx)
            else:
                notifications = Notification.objects.filter(user=request.user, tag__contains='post')
        if item_type=="circle":
            notifications = Notification.objects.filter(user=request.user, tag__contains='group')
        if item_type=="dossier":
            notifications = Notification.objects.filter(user=request.user, tag__contains='dossier')
        if item_type=="event":
            notifications = Notification.objects.filter(user=request.user, tag__contains='event')
        if item_type=="message":
            notifications = Notification.objects.filter(user=request.user, tag__contains='message')
        with transaction.atomic():
            if notifications:
                for notification in notifications:
                    serialized = NotificationSerializer(instance=notification, data={'read':True}, partial=True)
                    serialized.is_valid(raise_exception=True)
                    serialized.save()
        return Response({'message':'ok'})