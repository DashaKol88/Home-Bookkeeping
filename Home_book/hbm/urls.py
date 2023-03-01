from django.urls import path
from django.contrib.auth import views as auth_views
from . import views, api_views

urlpatterns = [
    path('', views.index, name='index'),

    path('login/', auth_views.LoginView.as_view(template_name='hbm/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='hbm/logout.html'), name='logout'),
    path('register/', views.register, name='register'),
    path('latest/', views.latest, name="latest"),
    path('add_transaction/', views.add_transaction, name='add_transaction'),
    path('del_transaction/<int:transaction_id>', views.del_transaction, name='del_transaction'),
    path('transaction_statistic/', views.transaction_statistic, name='transaction_statistic'),
    path('planned/transactions', views.planned_transactions, name='planned_transactions'),
    path('home/', views.home, name='home'),
    path('api/categories/', api_views.categories, name="categories"),
    path('api/transaction_latest/', api_views.transaction_latest, name="transaction_latest"),
    path('api/transaction_filter/', api_views.transaction_filter, name="transaction_filter"),
    path('api/transaction_add/', api_views.transaction_add, name="transaction_add"),

]
