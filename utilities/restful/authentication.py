from django.utils.translation import ugettext_lazy as _
from rest_framework.authentication import TokenAuthentication as BaseTokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


class TokenAuthentication(BaseTokenAuthentication):
    """
    Token authentication based on user model. the token saved and included in model
    make sure the user model have field called "token"

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:

        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """

    def get_model(self):
        if self.model is not None:
            return self.model
        from django.contrib.auth import get_user_model
        return get_user_model()

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            user = model.objects.get(token=key)
        except model.DoesNotExist:
            raise AuthenticationFailed(_('This token is Invalid or expire.'))

        if not user.is_active:
            raise AuthenticationFailed(_('Your account is inactive or deleted.'))

        return user, None
