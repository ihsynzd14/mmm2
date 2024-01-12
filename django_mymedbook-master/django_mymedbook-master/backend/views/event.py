from django.db import transaction

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError, NotFound

from backend.serializers import *
from backend.models import *
from backend.utils import handle_upload,handle_upload_document, download_remote_file, MEDIA_AVATAR, MEDIA_TERAPIE, MEDIA_EVENTI

from datetime import datetime
import urllib


class UploadEvent(APIView):
    permission_classes = (IsAuthenticated, )
    parser_classes = (FileUploadParser, MultiPartParser)

    def post(self, request):
        upload = request.data['file']
        pk = request.query_params.get('pk')

        try:
            user = UserProfile.objects.get(pk=request.query_params.get('user_id'))
        except UserProfile.DoesNotExist:
            user = request.user

        if pk:
            try:
                event = Event.objects.get(pk=int(pk))
            except Event.DoesNotExist:
                Event.DoesNotExist("Event not found")
        else:
            event = Event.objects.create(name="Event", user=user)

        document = Document.objects.create(
            document=upload
        )

        event.attachments.add(document)
        event.save()

        ''' field = document.document

        handle_upload_document(field, upload, MEDIA_EVENTI) '''
        context = {'request': request}
        event = EventSerializer(
            context=context, instance=event).data
        return Response(event)
