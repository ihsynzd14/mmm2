from django.db import transaction

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FileUploadParser
from rest_framework.pagination import PageNumberPagination

from backend import serializers
from backend.models import *
from backend.utils import handle_upload

import json

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit_elem'
    max_page_size = 10
    paginate_by = 10

class UploadConversations(APIView):
    permission_classes = (IsAuthenticated, )
    parser_classes = (FileUploadParser, )

    def post(self, request, pk):
        try:
            field = Conversation.objects.get(pk=pk).image
        except Conversation.DoesNotExist:
            raise ValidationError({'message': "conversation does not exist"})
        try:
            upload = request.data['file']
        except:
            raise ValidationError({'message': "file not found"})

        handle_upload(field, upload, 'conversations')

        return Response({'Message': 'ok'})


class conversationsWithMessage(APIView):
    permission_classes = (IsAuthenticated, )
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        user = request.user
        # tutte le conversazioni in cui l'utente loggato risulta attivo
        conversations = Conversation.objects.filter(
            usersconversations__user=user, usersconversations__active=True)
        serialized = serializers.ConversationWithMessagesSerializer(
            conversations, many=True).data
        return Response(serialized)


class deactivateConversation(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        conversation = request.data['conversation']
        userConversation = UsersConversations.objects.get(
            conversation=conversation, user=request.user)
        userConversation.active = False
        userConversation.save()

        return Response({'Message': 'user deactivate successfully from conversation'})
