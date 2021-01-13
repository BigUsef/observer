from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin

from corporations.api.serializers import ListEmployeeSerializer
from corporations.models import Employee


class EmployeeViewSet(ListModelMixin, GenericViewSet):
    model = Employee
    queryset = Employee.objects.all()
    serializer_class = ListEmployeeSerializer
