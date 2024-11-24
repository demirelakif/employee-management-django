from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin paneli
    path('api/', include('core.urls')),  # attendance uygulamasındaki URL'leri bağlama
]
