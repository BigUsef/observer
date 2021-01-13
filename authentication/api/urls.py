from rest_framework.routers import DefaultRouter

from authentication.api.views import FacilityStaffAuthViewSet, UsersViewSet

app_name = 'auth'

router = DefaultRouter()
router.register('facility-staff', FacilityStaffAuthViewSet, basename='facility_staff')
router.register('', UsersViewSet, basename='users')

urlpatterns = router.urls
