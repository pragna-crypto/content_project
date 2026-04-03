from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard_view, name='dashboard'),
    path('history/', views.history_list_view, name='history'),
    path('history/<int:pk>/', views.history_detail_view, name='history_detail'),
    path('api/analyze/', views.analyze_text_api, name='analyze_api'),
]
