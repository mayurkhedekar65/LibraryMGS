from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count, Sum
from .models import Book, Transaction, Member
from .forms import IssueBookForm, MemberSignUpForm, BookForm

def index(request):
    """Homepage: Display a list of all available books with search."""
    query = request.GET.get('q')
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) | 
            Q(author__icontains=query) |
            Q(genre__icontains=query)
        )
    else:
        books = Book.objects.all().order_by('title')
    
    return render(request, 'index.html', {'books': books, 'search_query': query})

@login_required
def member_dashboard(request):
    """User dashboard showing their borrowed books."""
    try:
        member = request.user.member_profile
        transactions = Transaction.objects.filter(member=member).order_by('-issue_date')
        return render(request, 'member_dashboard.html', {'transactions': transactions})
    except Member.DoesNotExist:
        # Redirect staff to admin dashboard if they accidentally go here
        if request.user.is_staff:
            return redirect('admin_dashboard')
        messages.error(request, "You do not have a member profile linked.")
        return redirect('index')

# --- NEW ADMIN DASHBOARD VIEW ---
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    """Central hub for Librarians to manage the system."""
    
    # 1. Calculate Stats
    total_books = Book.objects.aggregate(total=Sum('total_copies'))['total'] or 0
    books_issued = Transaction.objects.filter(status='Issued').count()
    books_available = total_books - books_issued
    total_members = Member.objects.count()
    
    # 2. Get Recent Activity
    recent_transactions = Transaction.objects.select_related('book', 'member__user').order_by('-issue_date')[:5]
    
    # 3. Check for Overdue Books
    overdue_transactions = Transaction.objects.filter(
        status='Issued', 
        expected_return_date__lt=timezone.now()
    ).count()

    context = {
        'total_books': total_books,
        'books_issued': books_issued,
        'books_available': books_available,
        'total_members': total_members,
        'recent_transactions': recent_transactions,
        'overdue_count': overdue_transactions,
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def issue_book(request):
    """Admin view to issue a book."""
    if request.method == 'POST':
        form = IssueBookForm(request.POST)
        if form.is_valid():
            book = form.cleaned_data['book_obj']
            member = form.cleaned_data['member_obj']
            
            Transaction.objects.create(book=book, member=member)
            
            # Decrease available copies
            book.available_copies -= 1
            book.save()
            
            messages.success(request, f"Book '{book.title}' issued to {member.user.username}.")
            return redirect('issue_book')
    else:
        form = IssueBookForm()
    
    return render(request, 'issue_book.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def return_book(request, transaction_id):
    """Admin action to return a book."""
    transaction = get_object_or_404(Transaction, id=transaction_id)
    
    if transaction.status == 'Returned':
        messages.warning(request, "This book is already returned.")
        return redirect('all_transactions')

    transaction.status = 'Returned'
    transaction.actual_return_date = timezone.now()
    
    # Calculate fine logic ($1 per day overdue)
    if transaction.actual_return_date > transaction.expected_return_date:
        overdue_days = (transaction.actual_return_date - transaction.expected_return_date).days
        transaction.fine_amount = overdue_days * 1.00
        
    transaction.save()
    
    # Increase available copies
    transaction.book.available_copies += 1
    transaction.book.save()
    
    messages.success(request, f"Book returned. Fine: ${transaction.fine_amount}")
    return redirect('all_transactions')

@login_required
@user_passes_test(lambda u: u.is_staff)
def all_transactions(request):
    """Admin view to see active loans."""
    transactions = Transaction.objects.filter(status='Issued').order_by('expected_return_date')
    return render(request, 'all_transactions.html', {'transactions': transactions})

def signup(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = MemberSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Log them in immediately after signup
            messages.success(request, "Registration successful! Welcome to LibMGS.")
            return redirect('dashboard')
    else:
        form = MemberSignUpForm()
    
    return render(request, 'registration/signup.html', {'form': form})

# --- NEW DBMS CRUD OPERATIONS ---

@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_books(request):
    """READ: View all books with edit/delete options."""
    books = Book.objects.all()
    return render(request, 'manage_books.html', {'books': books})

@login_required
@user_passes_test(lambda u: u.is_staff)
def add_book(request):
    """INSERT: Add a new book to the database."""
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Book added successfully!")
            return redirect('manage_books')
    else:
        form = BookForm()
    return render(request, 'book_form.html', {'form': form, 'title': 'Add New Book'})

@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_book(request, pk):
    """UPDATE: Modify an existing book."""
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, "Book updated successfully!")
            return redirect('manage_books')
    else:
        form = BookForm(instance=book)
    return render(request, 'book_form.html', {'form': form, 'title': 'Edit Book'})

@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_book(request, pk):
    """DELETE: Remove a book from the database."""
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, "Book deleted successfully!")
        return redirect('manage_books')
    return render(request, 'book_confirm_delete.html', {'book': book})