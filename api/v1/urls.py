from django.urls import path, include
from rest_framework import routers, serializers, viewsets
from . import views

router = routers.DefaultRouter()

urlpatterns = [
    path('v1/', include(router.urls)),
]
