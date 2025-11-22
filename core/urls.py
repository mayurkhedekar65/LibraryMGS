from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.member_dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),  # <--- Added Signup URL
    path('issue/', views.issue_book, name='issue_book'),
    path('transactions/', views.all_transactions, name='all_transactions'),
    path('return/<int:transaction_id>/', views.return_book, name='return_book'),
]