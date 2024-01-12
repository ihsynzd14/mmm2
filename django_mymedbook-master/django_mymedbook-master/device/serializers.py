from django.db import transaction

from rest_framework import permissions, routers, serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied, APIException, NotFound
from rest_framework.pagination import PageNumberPagination

from backend.models import *
from backend.serializers import *
from device.models import Device, Notification
from collections import OrderedDict


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 10
    paginate_by = 10


class AllFieldsSerializer(serializers.ModelSerializer):

    def get_fields(self):
        original_fields = super(AllFieldsSerializer, self).get_fields()
        fields = OrderedDict()
        for k, v in original_fields.items():
            fields['pk' if k == 'id' else k] = v
        return fields

###GRUPPI###
class NotificationSerializer(AllFieldsSerializer):
    #group = EventSerializerBase()
    #user = UserProfileSerializer()
    #friend_user = UserProfileSerializerForEvent()

    class Meta:
        model = Notification
        fields = '__all__'


class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def list(self, request):
        ##contatore bacheca
        notifications = {
            'post':{
                'count': Notification.objects.filter(user=self.request.user, tag__contains='post', read=False).count()
            },
            'circle':{
                'count': Notification.objects.filter(user=self.request.user, tag__contains='group', read=False).count()
            },
            'dossier':{
                'count': Notification.objects.filter(user=self.request.user, tag__contains='dossier', read=False).count()
            },
            'event':{
                'count': Notification.objects.filter(user=self.request.user, tag__contains='event', read=False).count()
            },
            'message':{
                'count': Notification.objects.filter(user=self.request.user, tag__contains='message', read=False).count()
            }
        }
        return Response(notifications)

    def destroy(self, request, *args, **kwargs):
        notification_id = self.kwargs['pk']
        try:
            notification = Notification.objects.get(pk=self.kwargs['pk']).delete()
        except Notification.DoesNotExist:
            raise NotFound('Notification not found')

        return Response({'message':'Notification deleted succesfully'})