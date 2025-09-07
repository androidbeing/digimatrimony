from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('matches/', views.matches, name='matches'),
    path('shortlisted/', views.shortlisted, name='shortlisted'),
    path('notifications/', views.notifications, name='notifications'),
    path('profile/', views.profile, name='profile'),
    path('profile/<int:pk>/', views.profile_detail, name='profile_detail'),
    path('profile/photos/upload/', views.profile_photo_upload, name='profile_photo_upload'),
    path('profile/photos/<int:pk>/set_primary/', views.profile_photo_set_primary, name='profile_photo_set_primary'),
    path('profile/photos/<int:pk>/delete/', views.profile_photo_delete, name='profile_photo_delete'),
]