from django.utils.translation import ugettext_lazy as _
from rest_framework.compat import unicode_http_header
from rest_framework.exceptions import NotAcceptable
from rest_framework.versioning import BaseVersioning


class APIVersion:
    @staticmethod
    def cast_version(version: str) -> tuple:
        cast_value = version.split('.')
        if len(cast_value) != 4:
            raise ValueError(_('This version has wrong format, Please use right format EX:0.0.0.0'))
        version_numbers = tuple(int(num) for num in cast_value)
        return version_numbers

    def __init__(self, version: str):
        self.header = version
        self.release, self.major, self.minor, self.patch = self.cast_version(version)

    def __str__(self):
        return f'V{self.header}'

    def __repr__(self):
        return f'<APIVersion {self.header}>'

    def __eq__(self, other) -> bool:
        return True if self.release == other.release and self.major == other.major else False

    def __ne__(self, other) -> bool:
        return True if self.release != other.release or self.major != other.major else False

    def __gt__(self, other) -> bool:
        if self.release > other.release:
            return True
        elif self.release == other.release:
            if self.major > other.major:
                return True
            elif self.major == other.major and self.minor > other.minor:
                return True
        return False

    def __ge__(self, other) -> bool:
        if self.release > other.release:
            return True
        elif self.release == other.release:
            if self.major > other.major:
                return True
            elif self.major == other.major and self.minor >= other.minor:
                return True
        return False

    def __lt__(self, other) -> bool:
        if self.release < other.release:
            return True
        elif self.release == other.release:
            if self.major < other.major:
                return True
            elif self.major == other.major and self.minor < other.minor:
                return True
        return False

    def __le__(self, other) -> bool:
        if self.release < other.release:
            return True
        elif self.release == other.release:
            if self.major < other.major:
                return True
            elif self.major == other.major and self.minor <= other.minor:
                return True
        return False

    def is_valid(self, version: str) -> bool:
        """
        this method used to ensure this version is released after passed version, and compare all version numbers
        :param version: string version want to compare current version with
        :return: boolean flag represent result
        """
        compared = APIVersion(version)
        return self >= compared and self.patch >= compared.patch


class APIHeaderVersioning(BaseVersioning):
    empty_version_message = _('API version credentials were not provided.')
    invalid_version_message = _('Invalid version in header, Please use valid api version')

    def is_allowed_version(self, version: APIVersion) -> bool:
        # make sure request version greatest than the default version
        if self.default_version and not version.is_valid(self.default_version):
            return False

        if not self.allowed_versions:
            return True
        allowed_status = [version == APIVersion(v) for v in self.allowed_versions]
        return any(allowed_status)

    def determine_version(self, request, *args, **kwargs):
        version = request.META.get('HTTP_API_VERSION', self.default_version)
        if not version:
            raise NotAcceptable(self.empty_version_message)

        unicode_version = unicode_http_header(version)
        try:
            version_obj = APIVersion(version=unicode_version)
            if not self.is_allowed_version(version_obj):
                raise NotAcceptable(self.invalid_version_message)
            return version_obj
        except ValueError as ex:
            raise NotAcceptable(ex)
