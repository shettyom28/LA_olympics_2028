from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    
    # User Profiles
    path('profile/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.profile_detail, name='profile_detail'),
    
    # Authentication
    path('register/', views.user_registration, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]