from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Book, Transaction, Member
from .forms import IssueBookForm, MemberSignUpForm

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
        # Fallback if a user exists but has no member profile (shouldn't happen with new signup flow)
        messages.error(request, "You do not have a member profile linked.")
        return redirect('index')

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