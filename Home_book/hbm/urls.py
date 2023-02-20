from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='hbm/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='hbm/logout.html'), name='logout'),
    path('latest/', views.latest, name="latest"),
]
