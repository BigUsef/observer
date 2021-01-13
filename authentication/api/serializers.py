from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from corporations.models import Facility

User = get_user_model()


class FacilityStaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = 'token', 'username', 'full_name',


class FacilityStaffAuthSerializer(serializers.Serializer):
    facility = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, max_length=32)

    class Meta:
        fields = 'facility', 'username', 'password',

    def validate_facility(self, value):
        try:
            return Facility.objects.get(is_active=True, uid=value)
        except Facility.DoesNotExist:
            raise serializers.ValidationError(_(
                'This facility no longer exists or has been deactivated, '
                'please contact with support for more details'
            ))

    def validate_username(self, value):
        try:
            user = User.objects.prefetch_related('facility_staff').get(username=value, is_active=True)
            # check if user is Employee
            if not hasattr(user, 'facility_staff'):
                raise serializers.ValidationError(_('Unable to use this service, you not have right permissions'))
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError(_(
                'This user no longer exists or has been deactivated, '
                'please contact with support for more details'
            ))

    def create(self, validated_data):
        user = validated_data.get('username')
        facility = validated_data.get('facility')

        if user.facility_staff.facility_id == facility.id:
            is_password = user.check_password(validated_data.get('password'))
            if not is_password:
                raise serializers.ValidationError(_(
                    'You have entered wrong credentials, please retry with case-sensitive credentials'
                ))
            # generate token if user not have token
            if not user.token:
                user.generate_token(commit=True)
            return user
        else:
            raise serializers.ValidationError(_(
                'You are not associated to this facility, '
                'please get help from facility admin'
            ))

    def update(self, instance, validated_data):
        raise serializers.ValidationError('Unexpected action triggered')

    def to_representation(self, instance: User):
        rep_serializer = FacilityStaffProfileSerializer(instance=instance)
        return rep_serializer.data


class FacilityStaffChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=32, required=True)

    class Meta:
        fields = 'password',

    def validate_password(self, value):
        user = self.instance
        if user and user.check_password(value):
            raise serializers.ValidationError(_("You can't use same password again."))
        return value

    def create(self, validated_data):
        raise serializers.ValidationError('Unexpected action triggered')

    def update(self, instance, validated_data):
        instance.set_password(validated_data.get('password'))
        instance.save()
        return instance

    def to_representation(self, instance):
        return dict()


class AuthActivateAccountSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    first_name = serializers.CharField(max_length=30, required=True)
    last_name = serializers.CharField(max_length=90, required=True)
    password = serializers.CharField(max_length=32, required=True)

    def validate_username(self, value):
        if value != self.instance.username and not User.objects.check_username_availability(value):
            raise serializers.ValidationError('this username belong to another user')
        return value

    def create(self, validated_data):
        raise serializers.ValidationError('Unexpected action triggered')

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name')
        instance.last_name = validated_data.get('last_name')
        instance.set_password(validated_data.get('password'))
        instance.is_verified = True
        instance.generate_token(commit=False)
        instance.save()
        return instance

    def to_representation(self, instance):
        return dict()
