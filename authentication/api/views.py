from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django.utils.translation import ugettext_lazy as _

from authentication.api.serializers import (
    FacilityStaffAuthSerializer,
    FacilityStaffChangePasswordSerializer, AuthActivateAccountSerializer
)

User = get_user_model()


class FacilityStaffAuthViewSet(GenericViewSet):
    serializer_class = FacilityStaffAuthSerializer

    def get_permissions(self):
        if self.action == 'login':
            self.permission_classes = AllowAny,
        return super().get_permissions()

    @action(methods=['post'], detail=False)
    def login(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['put'], detail=False, url_path='change-password')
    def change_password(self, request, *args, **kwargs):
        serializer = FacilityStaffChangePasswordSerializer(data=request.data, instance=self.request.user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UsersViewSet(GenericViewSet):
    serializer_class = FacilityStaffAuthSerializer

    @action(
        methods=['get', 'put'],
        detail=False,
        url_path=r'activation/(?P<code>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})',
        permission_classes=[AllowAny]
    )
    def activation(self, request, code: str, *args, **kwargs):
        """
        this api action response on activate any user on system, by using activation code send on email
        :param request: request object
        :param code: code string sending on email
        :param args:
        :param kwargs:
        """
        user_data = cache.get(code)
        # make sure the code still filed
        if not user_data:
            return Response(_('Invalid activation Link.'), status=status.HTTP_404_NOT_FOUND)

        # on get request send user data
        if request.method.lower() == 'get':
            return Response(data=user_data, status=status.HTTP_200_OK)

        # handle save new data post method
        try:
            instance = User.objects.get(id=user_data['id'])
            # check if user is verified before
            if instance.is_verified:
                return Response(_('Your account is already verified.'), status=status.HTTP_400_BAD_REQUEST)

            serializer = AuthActivateAccountSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # delete cache code after activation process finish
            cache.delete(code)
            return Response(_('Account has been activated successfully'), status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                _('Error in activation process, please contact with support.'),
                status=status.HTTP_400_BAD_REQUEST
            )
