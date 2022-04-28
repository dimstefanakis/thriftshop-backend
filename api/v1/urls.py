from django.urls import path, include
from rest_framework import routers, serializers, viewsets

from . import views

router = routers.DefaultRouter()
router.register(r'listing', views.MVPViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/user/me/', views.get_user, name="get_user"),
    path('v1/get_twitter_tokens/', views.get_twitter_tokens, name="twitter_tokens"),
    # used after registration flow
    path('v1/get_twitter_access_tokens/',
         views.get_twitter_access_tokens, name="get_twitter_access_tokens"),
]

