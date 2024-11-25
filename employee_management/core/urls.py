from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmployeeAuthToken,
    RegisterView,
    EmployeeApi,
    AttendanceRecordViewSet,
    LeaveRequestViewSet,
    EmployeeLogoutView,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Employee Management API",
        default_version='v1',
        description="API documentation for employee management system",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="demirel.akif@hotmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)


# Router tanımlayın
router = DefaultRouter()
router.register(r'attendance', AttendanceRecordViewSet, basename='attendance')
router.register(r'leaveRequest', LeaveRequestViewSet, basename='leaveRequest')

# URL'leri tanımlayın
urlpatterns = [
    path('login/', EmployeeAuthToken.as_view(), name='login'),
    path('logout/', EmployeeLogoutView.as_view(), name='logout'),  
    path('register/', RegisterView.as_view(), name='register'),
    path('employee/', EmployeeApi.as_view(), name='employee'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('leaveRequest/<int:pk>/approve/', LeaveRequestViewSet.as_view({'post': 'approve_leave_request'}), name='approve_leave_request'),
    path('leaveRequest/<int:pk>/reject/', LeaveRequestViewSet.as_view({'post': 'reject_leave_request'}), name='reject_leave_request'),
    path('', include(router.urls)),  # Router ile oluşturulan tüm endpoint'ler
]
