from django.db import transaction

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError

from backend.serializers import *
from backend.models import *


class AttributeValues(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user
        guest_id = request.query_params.get('user_id', None)
        if guest_id is not None:
            try:
                user = UserProfile.objects.get(pk=guest_id)
            except UserProfile.DoesNotExist:
                raise ValidationError('User not found')

        results = []
        #prelevo la struttura dell'utente loggato, se e' sia CDV sia MMB prendo CDV
        structure_user = [1]
        if len(request.user.structuremembership_set.all())>0:
            for structure in request.user.structuremembership_set.all():
                structure_user.append(structure.structure_id)
        for group in AttributeGroup.objects.filter(structure__in=structure_user).exclude(structure__code_type='fast_help').order_by('sorting'):
            serialized = AttributeGroupSerializer(instance=group).data
            results.append(serialized)
            serialized['attributes'] = []
            group_attribute_values = {}
            #query per prendere tutti gli attribute (non i valori) che andrebbero in quel gruppo
            for attribute in Attribute.objects.filter(group=group).order_by('sorting'):
                serialized_value={
                    'attribute':AttributeSerializer(instance=attribute).data,
                    'value':None,
                }
                if attribute.datatype == 'enum':
                    queryset = Enum.objects.filter(attribute=attribute)
                    serialized_value['enum'] = EnumSerializer(queryset, many=True).data

                if attribute.datatype == 'year_with_text':
                    serialized_value['other'] = None

                serialized['attributes'].append(serialized_value)
                group_attribute_values[attribute.pk] = serialized_value

            #query per prendere tutti gli i valori che andrebbero in quel gruppo
            for attribute_value in AttributeValue.objects.filter(attribute__group=group, user=user):
                attribute = attribute_value.attribute
                serialized_value = AttributeValueSerializer(instance=attribute_value).data
                print serialized_value
                if attribute.datatype=='enum':
                    serialized_value['value']=[attribute_value.enum.pk]
                if group_attribute_values[attribute.pk].get('value',None)==None:
                    #merge tra group_attribute_values[attribute.pk] e serialized_value
                    #TODO: controllare se esista un metodo piu' efficente per realizzarlo
                    for field in serialized_value:
                        group_attribute_values[attribute.pk][field] = serialized_value[field]
                else:
                    if attribute.datatype=='enum':
                        group_attribute_values[attribute.pk]['value'] += serialized_value['value']
                    else:
                        group_attribute_values[attribute.pk]['value'] = serialized_value['value']

        return Response(results)


class AttributeSchema(APIView):

    def get(self, request):

        attrGroup_instance = AttributeGroup.objects.all().order_by('sorting')
        result = []
        for item in attrGroup_instance:
            attributeGroup = AttributeGroupSerializer(instance=item).data
            attributes = Attribute.objects.filter(group=item)
            attributeGroup['attributes'] = []
            result_attribute = []
            for i in attributes:
                attribute = AttributeSerializer(instance=i).data
                if attribute['datatype'] == 'enum':
                    values = Enum.objects.filter(attribute=i)
                    attribute['enum'] = EnumSerializer(
                        instance=values, many=True).data
                result_attribute.append(attribute)
            attributeGroup['attributes'] = result_attribute
            result.append(attributeGroup)
        return Response(result)
