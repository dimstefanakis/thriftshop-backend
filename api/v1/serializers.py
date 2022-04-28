from rest_framework import serializers
from mvp.models import Mvp, CloudType, Platform, Industry, TechStack, Service, Hosting
from accounts.models import UserProfile


class CloudTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CloudType
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
    cloud_types = CloudTypeSerializer(many=True)
    platforms = PlatformSerializer(many=True)
    industries = IndustrySerializer(many=True)
    tech_stack = TechStackSerializer(many=True)
    services = ServiceSerializer(many=True)
    hosting = HostingSerializer(many=True)

    class Meta:
        model = Mvp
        fields = ('id', 'name', 'one_liner', 'description', 'validation', 'total_users', 'active_users',
                'github_project_url', 'website_url', 'credit', 'cloud_types', 'platforms', 'industries', 'tech_stack',
                'services', 'hosting', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at', 'id')


class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    def get_avatar(self, profile):
        if profile.avatar:
            return profile.avatar.url

    def get_name(self, profile):
        return profile.user.first_name + ' ' + profile.user.last_name

    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'name', 'twitter_avatar', 'avatar', 'website_url', 'github_url',
                  'description')
        read_only_fields = ('id',)
