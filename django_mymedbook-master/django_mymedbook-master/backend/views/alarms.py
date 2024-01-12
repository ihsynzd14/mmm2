from django.db import transaction

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError

from backend.serializers import *
from backend.models import *

class AlarmToggleActive(APIView):

    def post(self, request):
        user = request.user

        alarm_id = request.query_params.get('alarm_id', None)
        if alarm_id is None:
            raise ValidationError('Invalid alarm')

        active = request.data.get('handled', None)
        if active is None:
            raise ValidationError('Invalid data')

        try:
            alarm = Alarm.objects.get(pk=alarm_id)
        except Alarm.DoesNotExist:
            raise ValidationError('Alarm not found')

        if active == 'true' or active == True:
            alarm.handled = True
            alarm.handler = user
        else:
            alarm.handled = False
            alarm.handler = None

        alarm.save()

        return Response({'message':'ok'})

class AlarmFilter(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user
        dateI = request.query_params.get('dateI')
        dateF = request.query_params.get('dateF')
        if dateI:
            alarms = Alarm.objects.filter(date__gte=dateI)
        if dateF:
            alarms = alarms.objects.filter(date__lte=dateF)

        return Response(AlarmSerializer(instance=alarms, many=True).data)