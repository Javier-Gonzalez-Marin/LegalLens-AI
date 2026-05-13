from django.contrib import admin
from django.urls import path, include # Importa 'include'
from . import views
from django.contrib.auth import views as auth_views # Importa las vistas de auth

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rutas de Login y Logout
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload_contract, name='upload_contract'),

    path('delete/<int:contrato_id>/', views.delete_contract, name='delete_contract'),
]