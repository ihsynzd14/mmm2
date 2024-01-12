from django.db import transaction

from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from backend.models import *
from backend.serializers import *
from backend.utils import handle_upload, handle_upload_document


class UploadPost(APIView):
    permission_classes = (IsAuthenticated, )
    parser_classes = (FileUploadParser, )

    def post(self, request):
        data = request.data.copy()
        try:
            post = Post.objects.get(pk=request.query_params.get('pk'))
        except KeyError, Post.DoesNotExist:
            raise ValidationError({'message': "Post does not exist"})

        try:
            data['document'] = request.data['file']
        except:
            raise ValidationError({'message': "file not found"})

        doc = DocumentSerializer(data=data, partial=True)
        doc.is_valid(raise_exception=True)
        #handle_upload_all(doc.document, upload, 'documents')
        doc.save(post=post)
        '''for circle in field.circle.all():
            try:
                circle_instance = Circle.objects.get(pk=circle.pk)
            except Circle.DoesNotExist:
                ValidationError('Circle not found')
            for user in circle.circleaffiliation_set.all():
                user_aff = UserProfile.objects.get(pk=user.user_id)
                notifications = Notification.createPostNotifications(request.user, Notification.Type.CREATE_POST, circle, field, pk=pk)
                send_mail(self, '[MMB] nuovo post ', 'E\' stato condiviso un nuovo post con te. Accedi subito a www.mymedbook.it', user_aff.email)
        '''
        return Response({'Message': 'ok'})