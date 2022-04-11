from rest_framework import serializers
from mvp.models import Mvp


class MvpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mvp
        fields = ('id', 'name', 'one_liner', 'description',
                  'github_project_url', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at', 'id')
