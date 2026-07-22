"""
Main URL configuration for Expense Tracker project.
Connects the accounts (auth) app and expenses dashboard routes here.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django default Admin site for managing users/data directly in browser
    path('admin/', admin.site.urls),

    # Our custom authentication routes: signup/login/logout pages
    path('', include('accounts.urls')),  # Homepage is login/signup page

    # Main expense tracking dashboard (requires login)
    path('expenses/', include('expenses.urls')),  # Dashboard with filtering + chart
]
