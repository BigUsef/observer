from rest_framework.routers import DefaultRouter

from corporations.api.views import EmployeeViewSet

app_name = 'corporations'

router = DefaultRouter()
router.register('employee', EmployeeViewSet, basename='employee')

urlpatterns = router.urls
