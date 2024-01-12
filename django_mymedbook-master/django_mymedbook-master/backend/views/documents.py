from django.db import transaction

from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from backend.models import *
from backend.serializers import *
from backend.utils import handle_upload, handle_upload_document


class UploadDossier(APIView):
    permission_classes = (IsAuthenticated, )
    parser_classes = (FileUploadParser, )

    def post(self, request, pk):
        try:
            dossier = Dossier.objects.get(pk=pk)
        except Dossier.DoesNotExist:
            raise ValidationError({'message': "Dossier does not exist"})

        doc = Document.objects.create(
            dossier=dossier,
            document=request.data['file']
        )
        #handle_upload_document(doc.document, upload, 'documents')
        ''' for circle in dossier.circle.all():
            for user in circle.circleaffiliation_set.all():
                user_aff = UserProfile.objects.get(pk=user.user_id)
                Notification.createGroupNotifications(request.user, Notification.Type.EDIT_DOSSIER, user_aff, circle)
                send_mail(self, '[MMB] dossier modificato ', 'Hanno modificato un dossier condiviso con te. Accedi subito a www.mymedbook.it', user_aff.email) '''

        return Response({'Message': 'ok'})
