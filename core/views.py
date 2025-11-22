from django.shortcuts import render
from .models import Book

def index(request):
    """
    Homepage: Display a list of all available books.
    """
    # Fetch all books from the database, ordered alphabetically by title
    books = Book.objects.all().order_by('title')
    
    context = {
        'books': books
    }
    return render(request, 'index.html', context)