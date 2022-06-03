from django.urls import path, include
from rest_framework import routers, serializers, viewsets

from . import views

router = routers.DefaultRouter()
router.register(r'listing', views.MVPViewSet)
router.register(r'failure_reasons', views.FailureReasonsViewSet)
router.register(r'industries', views.IndustriesViewSet)
router.register(r'tech_stacks', views.TechStacksViewSet)
router.register(r'services', views.ServicesViewSet)
router.register(r'hostings', views.HostingsViewSet)
router.register(r'platforms', views.PlatformsViewSet)
router.register(r'cloud_types', views.CloudTypesViewSet)
router.register(r'membership_plans', views.MembershipPlansViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/user/me/', views.get_user, name="get_user"),
    path('v1/user/me/update/', views.update_user_profile, name="update_profile"),
    path('v1/submit_mvp/', views.create_mvp_submission, name="submit_mvp"),
    path('v1/create_mvp_suggestion/', views.create_mvp_suggestion,
         name="create_mvp_suggestion"),
    path('v1/create_subscription/', views.create_subscription, name="submit_mvp"),
    path('v1/cancel_subscription/', views.cancel_subscription,
         name="cancel_subscription"),
    path('v1/get_twitter_tokens/', views.get_twitter_tokens, name="twitter_tokens"),
    # used after registration flow
    path('v1/get_twitter_access_tokens/',
         views.get_twitter_access_tokens, name="get_twitter_access_tokens"),
    path('v1/stripe_webhook/', views.stripe_webhook, name="stripe_webhook"),
]
