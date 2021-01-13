from rest_framework import serializers

from corporations.models import Employee


class ListEmployeeSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Employee
        fields = 'username', 'is_chief',
