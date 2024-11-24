from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmployeeAuthToken,
    RegisterView,
    EmployeeApi,
    AttendanceRecordViewSet,
    LeaveRequestViewSet,
    NotificationViewSet,
    EmployeeLogoutView,
)

# Router tanımlayın
router = DefaultRouter()
router.register(r'attendance', AttendanceRecordViewSet, basename='attendance')
router.register(r'leaveRequest', LeaveRequestViewSet, basename='leaveRequest')
router.register(r'notification', NotificationViewSet, basename='notification')

# URL'leri tanımlayın
urlpatterns = [
    path('login/', EmployeeAuthToken.as_view(), name='login'),
    path('logout/', EmployeeLogoutView.as_view(), name='logout'),  
    path('register/', RegisterView.as_view(), name='register'),
    path('employee/', EmployeeApi.as_view(), name='employee'),
    path('', include(router.urls)),  # Router ile oluşturulan tüm endpoint'ler
]
