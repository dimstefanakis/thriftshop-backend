from rest_framework import serializers
from mvp.models import Mvp
from accounts.models import UserProfile


class MvpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mvp
        fields = ('id', 'name', 'one_liner', 'description',
                  'github_project_url', 'created_at', 'updated_at')
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
