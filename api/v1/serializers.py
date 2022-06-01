from rest_framework import serializers
from mvp.models import Mvp, CloudType, Platform, Industry, TechStack, Service, Hosting, FailureReason
from membership.models import Membership, MembershipPlan, Subscription
from accounts.models import UserProfile


class MembershipPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipPlan
        fields = ['id', 'name', 'description', 'credit', 'interval']


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'membership_plan', 'status']


class CloudTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CloudType
        fields = ['name', 'id']


class FailureReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = FailureReason
        fields = ['name', 'id']


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ['name', 'id']


class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ['name', 'id']


class TechStackSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechStack
        fields = ['name', 'id']


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['name', 'id']


class HostingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hosting
        fields = ['name', 'id']


class MvpSerializer(serializers.ModelSerializer):
    user_profile = serializers.SerializerMethodField()
    preview_image = serializers.SerializerMethodField()
    cloud_types = CloudTypeSerializer(many=True)
    failure_reasons = FailureReasonSerializer(many=True)
    platforms = PlatformSerializer(many=True)
    industries = IndustrySerializer(many=True)
    tech_stack = TechStackSerializer(many=True)
    services = ServiceSerializer(many=True)
    hosting = HostingSerializer(many=True)

    def get_user_profile(self, mvp):
        return UserProfileSerializer(mvp.user.profile).data

    def get_preview_image(self, mvp):
        request = self.context.get('request')
        if request and mvp.preview_image:
            photo_url = mvp.preview_image.url
            return request.build_absolute_uri(photo_url)
        else:
            return None

    class Meta:
        model = Mvp
        fields = ('id', 'user_profile', 'name', 'one_liner', 'preview_image', 'description', 'validation', 'total_users', 'active_users',
                  'github_project_url', 'website_url', 'credit', 'cloud_types', 'platforms', 'industries', 'tech_stack',
                  'services', 'hosting', 'failure_reasons', 'code_score', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at', 'id')


class UserProfileSerializer(serializers.ModelSerializer):
    subscription = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    def get_avatar(self, profile):
        if profile.avatar:
            if 'spaceguy.webp' in profile.avatar.url and profile.twitter_avatar:
                return profile.twitter_avatar
            return profile.avatar.url

    def get_name(self, profile):
        return profile.user.first_name + ' ' + profile.user.last_name

    def get_subscription(self, profile):
        return SubscriptionSerializer(profile.subscriptions.last()).data

    def get_email(self, profile):
        return profile.user.email

    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'is_buyer', 'is_seller', 'email', 'name', 'twitter_avatar', 'avatar', 'website_url', 'github_url',
                  'description', 'subscription')
        read_only_fields = ('id', 'user', 'email', 'twitter_avatar', 'subscription')
