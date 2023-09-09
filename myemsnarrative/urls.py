from django.contrib import admin
from django.urls import path, include
from accounts import views


urlpatterns = [
    path('', include('main.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
    path("password-reset-complete/", views.password_reset_complete_view, name="password_reset_complete"),
]