from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group

from models import *

class StructureAffiliationInline(admin.TabularInline):
    model = StructureAffiliation
    extra = 1

class StructureMembershipInline(admin.TabularInline):
    model = StructureMembership
    extra = 1

class SerialCOCInline(admin.TabularInline):
    model = SerialCOC
    extra = 1

class AttributeGroupInline(admin.TabularInline):
    model = AttributeGroup
    extra = 1
    show_change_link = True


@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'max_members',
        'max_affiliates',
        'phone_number',
        'mobile_number',
        'code_type',
        'created',
        'modified'
    )
    #inlines = [AttributeGroupInline,StructureMembershipInline,SerialCOCInline]
    readonly_fields = ('created', 'modified')

class AttributeInline(admin.TabularInline):
    model = Attribute
    extra = 1
    show_change_link = True

@admin.register(AttributeGroup)
class AttributeGroupAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'structure',
        'created',
        'modified'
    )
    list_filter = ('structure',)
    readonly_fields = ('created', 'modified')
    inlines = [AttributeInline]

class EnumInline(admin.TabularInline):
    model = Enum


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    inlines = (EnumInline,)
    list_display = (
        'name',
        'datatype',
        'group',
        'sorting',
        'created',
        'modified'
    )
    list_filter = ('group',)
    readonly_fields = ('created', 'modified')


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'text_value',
        'boolean_value',
        'number_value',
        'date_value',
        'lifesaver',
        'attribute',
        'enum',
        'user',
        'created',
        'modified'
    )
    readonly_fields = ('created', 'modified')


@admin.register(Enum)
class EnumAdmin(admin.ModelAdmin):
    list_display = (
        'value',
        'attribute',
        'created',
        'modified'
    )
    readonly_fields = ('created', 'modified')


@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'created_by',
        'created',
        'modified'
    )
    readonly_fields = ('created', 'modified')


@admin.register(CircleAffiliation)
class CircleAffiliationAdmin(admin.ModelAdmin):
    list_display = (
        'created_by',
        'name',
        'user',
        'joined',
        'left',
        'created',
        'modified'
    )
    readonly_fields = ('created', 'modified')



@admin.register(StructureAffiliation)
class StructureAffiliationAdmin(admin.ModelAdmin):
    list_display = (
        'joined',
        'left',
        'user',
        'structure',
        'created',
        'modified'
    )
    list_filter = ('structure',)
    readonly_fields = ('created', 'modified')



@admin.register(StructureMembership)
class StructureMembershipAdmin(admin.ModelAdmin):
    list_display = (
        'joined',
        'left',
        'user',
        'structure',
        'created',
        'modified'
    )
    readonly_fields = ('created', 'modified')
    search_fields = ('user',)
    list_filter = ('structure',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['username','email', 'first_name', 'last_name', 'fiscal_code']
    list_display = (
        'username',
        'first_name',
        'last_name',
        'birthday',
        'fiscal_code',
        'plaintext_password',
        'active',
        'modified'
    )
    list_filter = ('active',)
    inlines = [StructureAffiliationInline, StructureMembershipInline]
    readonly_fields = ('username','password','plaintext_password','created', 'modified')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'user',
        'created',
        'modified'
    )
    readonly_fields = ('created', 'modified')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'post',
        'user',
        'created',
        'modified'
    )
    readonly_fields = ('created', 'modified')


@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'meta_info',
        'fiscal_code',
        'user',
        'created',
        'modified'
    )
    readonly_fields = ('created', 'modified')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'document',
        'desc',
        'meta_info',
        'dossier',
        'created',
        'modified'
    )
    readonly_fields = ('created', 'modified')


@admin.register(Therapy)
class TherapyAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'start_date',
        'end_date',
        'drug',
        'treatment_plan',
        'instructions',
        'active',
        'notification',
        'lifesaver',
        'doctor',
        'created',
        'modified'
    )
    readonly_fields = ('created', 'modified')


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'created',
        'modified'
    )
    readonly_fields = ('created', 'modified')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'desc',
        'start_date',
        'end_date',
        'notification',
        'authority',
        'address',
        'user',
        'event_type',
        'created',
        'modified'
    )
    readonly_fields = ('created', 'modified')


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = (
        'caption',
        'identifier',
        'structure',
        'created',
        'modified'
    )
    list_filter = ('structure',)
    readonly_fields = ('created', 'modified')


@admin.register(Alarm)
class AlarmAdmin(admin.ModelAdmin):
    list_display = (
        'message',
        'date',
        'handled',
        'caller',
        'sensor',
        'created',
        'modified'
    )
    list_filter = ('sensor',)
    readonly_fields = ('created', 'modified')


@admin.register(Serial)
class SerialAdmin(admin.ModelAdmin):
    list_display = (
        'MMTCode',
        'serial_tag',
        'created',
        'modified'
    )
    readonly_fields = ('created', 'modified')


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'created',
        'modified'
    )
    readonly_fields = ('created', 'modified')


@admin.register(MyMedTag)
class MyMedTagAdmin(admin.ModelAdmin):
    search_fields = ['code']
    list_display = (
        'code',
        'structure_affiliation',
        'structure_membership',
        'product_type',
        'active',
        'created',
        'modified'
    )
    readonly_fields = ('created', 'modified')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'text',
        'conversation',
        'created',
        'modified'
    )
    readonly_fields = ('created', 'modified')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = (
        'mhash',
        'created_by',
        'title',
        'image',
        'created',
        'modified'
    )
    readonly_fields = ('created', 'modified')

## ADMIN for COC ##

@admin.register(SerialCOC)
class SerialCOCAdmin(admin.ModelAdmin):
    list_display = (
        'duration',
        'serial',
        'valid',
        'start_date_validation',
        'affiliation',
        'structure',
        'created',
        'modified'
    )
    list_filter = ('structure',)
    readonly_fields = ('created', 'modified')

@admin.register(ActionCOC)
class ActionCOCAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'label',
        'action_type',
        'circle',
        'created',
        'modified'
    )
    readonly_fields = ('created', 'modified')

@admin.register(AssistanceRequest)
class AssistanceRequestAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'handled',
        'affiliation',
        'latlng',
        'created',
        'modified'
    )
    readonly_fields = ('created', 'modified')
