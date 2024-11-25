from django.contrib import admin
from django.urls import path, include
from employee_management import views  # HTML view'larını dahil et

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin paneli
    path('api/', include('core.urls')),  # attendance uygulamasındaki URL'leri bağlama
    path('login/', views.login_view, name='login'),  
    path('register/', views.register_view, name='register'),  
    path('', views.home_view, name='home'),  
    path('leave-request/', views.leave_request, name='leave_request'),  
]
