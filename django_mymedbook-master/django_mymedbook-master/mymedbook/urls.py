from django.conf.urls import include, url
from django.contrib import admin, staticfiles

admin.autodiscover()

from rest_framework import routers

from oauth2_provider import views as oauth2_views

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import auth

from backend import views as backend_views
from backend import serializers

from django.views.generic import TemplateView


router = routers.DefaultRouter()
router.register(r'group', serializers.GroupViewSet)
router.register(r'profile', serializers.UserProfileViewSet)
router.register(r'register', serializers.RegisterViewSet)
router.register(r'structure', serializers.StructureViewSet)
router.register(r'attributegroup', serializers.AttributeGroupViewSet)
router.register(r'attribute', serializers.AttributeViewSet)
router.register(r'enum', serializers.EnumViewSet)
router.register(r'circle', serializers.CircleViewSet)
router.register(r'circleaffiliation', serializers.CircleAffiliationViewSet)
router.register(r'structureaffiliation', serializers.StructureAffiliationViewSet)
router.register(r'structuremembership', serializers.StructureMembershipViewSet)
router.register(r'attributevalue', serializers.AttributeValueViewSet)
router.register(r'post', serializers.PostViewSet)
router.register(r'comment', serializers.CommentViewSet)
router.register(r'dossier', serializers.DossierViewSet)
router.register(r'document', serializers.DocumentViewSet)
router.register(r'therapy', serializers.TherapyViewSet)
router.register(r'event', serializers.EventViewSet)
router.register(r'event_type', serializers.EventTypeViewSet)
router.register(r'alarm', serializers.AlarmViewSet)
router.register(r'user', serializers.UserViewSet)
router.register(r'alluser', serializers.AllUserViewSet)
router.register(r'tags', serializers.MyMedTagViewSet)
router.register(r'tags_structure', serializers.MymedtagStructure)
router.register(r'products', serializers.ProductTypeViewSet)
router.register(r'conversation', serializers.ConversationViewSet)
router.register(r'messages', serializers.MessageViewSet)
router.register(r'users/MMBList', serializers.UserProfileForAdminViewSet)


BASE_API_URL_V1='api/v1/'

urls = [
    url(r'^oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^upload/profile/avatars/$', backend_views.UploadProfile.as_view()),
    url(r'^upload/guest/$', backend_views.UploadGuest.as_view()),
    url(r'^upload/dossier/(?P<pk>[0-9]+)/$', backend_views.UploadDossier.as_view()),
    url(r'^upload/post/$', backend_views.UploadPost.as_view()),
    url(r'^upload/therapy/$', backend_views.UploadTherapy.as_view()),
    url(r'^upload/events/$', backend_views.UploadEvent.as_view()),
    url(r'^attribute/values/$', backend_views.AttributeValues.as_view()),
    url(r'^attribute/schema/$',backend_views.AttributeSchema.as_view()),
    url(r'^profile/edit/$', backend_views.EditProfile.as_view()),
    url(r'^profile/editattributes/$', backend_views.EditProfileAttributes.as_view()),
    url(r'^mymedtag/$', backend_views.MyMedTagView.as_view()),
    url(r'^users/verificationGuest/$', backend_views.VerificationGuestExistence.as_view()),
    url(r'^users/members/register/$', backend_views.newMembership.as_view()),
    url(r'^users/family/register/$', backend_views.newAffiliationParent.as_view()),
    url(r'^users/family/affiliation/$', backend_views.addAffiliationParent.as_view()),
    url(r'^change_password/', backend_views.change_password.as_view()),
    # affiliations
    url(r'^users/affiliation/$',backend_views.UserAffiliationSingle.as_view()),
    url(r'^users/affiliations/$',backend_views.UsersAffiliationsList.as_view()),
    url(r'^users/affiliation/deactive/$',backend_views.DeactiveAffiliation.as_view()),
    url(r'^users/verifyAffiliation/$', backend_views.VerificationAffiliation.as_view()),
    #url(r'^users/MMBList/$',backend_views.UsersMMBList.as_view()),
    url(r'^users/listForChat/$',backend_views.UsersListForChat.as_view()),
    # alarms
    url(r'^alarm/toggleactive/$',backend_views.AlarmToggleActive.as_view()),
    url(r'^alarm/filter/$',backend_views.AlarmFilter.as_view()),
    # conversation&message
    url(r'^conversations/withmessages/$', backend_views.conversationsWithMessage.as_view()),
    url(r'^deactivateConversation/', backend_views.deactivateConversation.as_view()),
    #SOSTAGSMS
    url(r'^sostagsms$', backend_views.gestioneSOSTAGSMS.as_view()),
] + router.urls

password_urls = [
    url(r'^password/reset/$', backend_views.PasswordReset.as_view()),
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        backend_views.PasswordResetConfirm.as_view()),
    url(r'^activate_account/$',backend_views.UserActivateAccount.as_view()),
    # invio mail di attivazione
    url(r'^mail/activation/$', backend_views.sendMailActivation.as_view()),
]

COC_urls = [
    url(r'^profile/editattributes/$', backend_views.EditCOCProfileAttributes.as_view()),
    url(r'^attribute/values/$', backend_views.AttributeValuesCOC.as_view()),
    url(r'^structure/list/$',backend_views.COCList.as_view()),
    url(r'^actions/create/$',backend_views.SaveActions.as_view()),
    url(r'^actions/delete/$',backend_views.DeleteActions.as_view()),
    url(r'^actions/list/$',backend_views.SaveActions.as_view()),
    url(r'^serial/create/$',backend_views.SaveSerial.as_view()),
    url(r'^serial/list/$',backend_views.ListSerial.as_view()),
    url(r'^serial/allList/$',backend_views.AllListSerial.as_view()),
    url(r'^assistance/request/$',backend_views.SaveAssistanceRequest.as_view()),
    url(r'^assistance/list/$',backend_views.AssistanceList.as_view()),
    url(r'^assistance/toggleactive/$',backend_views.AssistanceToggleActive.as_view()),
    url(r'^assistance/filter/$',backend_views.AssistanceFilter.as_view()),
    url(r'^MMTCode/$',backend_views.ViewTagsAffiliation.as_view()),
]

urlpatterns = [
    url(r'^'+BASE_API_URL_V1+'COC/', include(COC_urls)),
    url(r'^users/', include(password_urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^api/v1/', include(urls)),
     url(r'^mymedtag/$', TemplateView.as_view(template_name="mymedtag.html")),
    url(r'^mmbalarm.php$',backend_views.orbitHandler),
    url(r'^'+BASE_API_URL_V1+'devices/', include('device.urls')),
]

if settings.DEBUG:
    urlpatterns += static('/media', document_root=settings.MEDIA_ROOT)
