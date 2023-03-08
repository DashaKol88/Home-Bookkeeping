from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='hbm/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='hbm/logout.html'), name='logout'),
    path('register/', views.register, name='register'),
    path('latest/', views.latest, name="latest"),
    path('add_transaction/', views.add_transaction, name='add_transaction'),
    path('del_transaction/<int:transaction_id>', views.del_transaction, name='del_transaction'),
    path('transaction_statistics/', views.transaction_statistics, name='transaction_statistics'),
    path('planned/transactions/', views.planned_transactions, name='planned_transactions'),
    path('planned/add_scheduled_transaction/', views.add_scheduled_transaction, name='add_scheduled_transaction'),
    path('planned/del_scheduled_transaction/<int:transaction_id>', views.del_scheduled_transaction, name='del_scheduled_transaction'),
    #path('planned/transaction_statistics/', views.planned_transaction_statistics, name='planned_transaction_statistics'),
    path('filter/', views.filter, name='filter'),
]
