from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('filter/', views.filter_expenses, name='filter_expenses'),
    path('reports/', views.reports, name='reports'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),
    path('delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
]