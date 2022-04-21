from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.signals import social_account_added, social_account_updated, pre_social_login
from allauth.account.signals import user_signed_up


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    description = models.CharField(max_length=240, blank=True, default='')
    avatar = models.ImageField(blank=True, upload_to='user/avatar')
    twitter_avatar = models.URLField(max_length=400, blank=True, default='')
    website_url = models.URLField(max_length=200, blank=True, default='')
    github_url = models.URLField(max_length=200, blank=True, default='')


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         profile = UserProfile.objects.create(user=instance)
#         if instance.socialaccount_set.exists():
#             sc_account = SocialAccount.objects.filter(user=instance, provider='twitter')

#             # sc_account = instance.sociallogin.account
#             if sc_account.exists():
#                 sc_account = sc_account.first()
#                 profile.avatar = sc_account.extra_data['profile_image_url']
#                 profile.website_url = sc_account.extra_data['url']
#                 profile.description = sc_account.extra_data['description']
#                 profile.save()


@receiver(user_signed_up)
def create_user_profile(request, user, **kwargs):
    profile = UserProfile.objects.create(user=user)
    if user.socialaccount_set.exists():
        sc_account = SocialAccount.objects.filter(
            user=user, provider='twitter')

        # sc_account = instance.sociallogin.account
        if sc_account.exists():
            sc_account = sc_account.first()
            profile.twitter_avatar = sc_account.extra_data['profile_image_url']
            profile.website_url = sc_account.extra_data['url']
            profile.description = sc_account.extra_data['description']
            profile.save()


@receiver(social_account_added)
def create_user_profile_after_social(request, sociallogin, **kwargs):
    sc_account = sociallogin.account
    profile = UserProfile.objects.filter(user=request.user.pk)
    if profile.exists():
        profile = profile.first()
    else:
        profile = UserProfile.objects.create(user=request.user)
    if sc_account.provider == 'twitter':
        profile.twitter_avatar = sc_account.extra_data['profile_image_url']
        profile.website_url = sc_account.extra_data['url']
        profile.description = sc_account.extra_data['description']
        profile.save()


@receiver(social_account_updated)
def update_user_profile_after_social(request, sociallogin, **kwargs):
    sc_account = sociallogin.account
    profile = UserProfile.objects.filter(user=request.user.pk)
    if profile.exists():
        profile = profile.first()
    else:
        profile = UserProfile.objects.create(user=request.user)
    if sc_account.provider == 'twitter':
        profile.twitter_avatar = sc_account.extra_data['profile_image_url']
        profile.website_url = sc_account.extra_data['url']
        profile.description = sc_account.extra_data['description']
        profile.save()


# @receiver(pre_social_login)
# def create_user_profile_after_social_login(request, sociallogin, **kwargs):
#     sc_account = sociallogin.account
#     profile = UserProfile.objects.filter(user=request.user.pk)
#     if profile.exists():
#         profile = profile.first()
#     else:
#         profile = UserProfile.objects.create(user=request.user)
#     if sc_account.provider == 'twitter':
#         profile.avatar = sc_account.extra_data['profile_image_url']
#         profile.website_url = sc_account.extra_data['url']
#         profile.description = sc_account.extra_data['description']
#         profile.save()
