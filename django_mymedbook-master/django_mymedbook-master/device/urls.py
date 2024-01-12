from django.conf.urls import include, url
from views import *
from serializers import *

router = routers.DefaultRouter()
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    url(r'^register/(?P<uuid>.*?)/$', RegisterDevice.as_view()),
    url(r'^bind/(?P<uuid>.*?)/$', BindDevice.as_view()),
    url(r'^unbind/(?P<uuid>.*?)/$', UnbindDevice.as_view()),
    url(r'^sendNotification/$', SendNotification.as_view()),
    url(r'^checkNotificationAsRead/', CheckNotificationFrontendAsRead.as_view()),
    url(r'^', include(router.urls)),
]
