from django.urls import path
from . import views

urlpatterns = [
    # Existing user/staff paths
    path('', views.index, name='index'),
    path('dashboard/', views.member_dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('issue/', views.issue_book, name='issue_book'),
    path('transactions/', views.all_transactions, name='all_transactions'),
    path('return/<int:transaction_id>/', views.return_book, name='return_book'),
    
    # --- NEW CRUD URLS (Book Management) ---
    path('books/manage/', views.manage_books, name='manage_books'),
    path('books/add/', views.add_book, name='add_book'),
    path('books/edit/<int:pk>/', views.edit_book, name='edit_book'),
    path('books/delete/<int:pk>/', views.delete_book, name='delete_book'),
]