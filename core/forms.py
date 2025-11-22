from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Book, Member
import uuid

class IssueBookForm(forms.Form):
    isbn = forms.CharField(label="Book ISBN", max_length=13, widget=forms.TextInput(attrs={'class': 'border rounded p-2 w-full'}))
    membership_id = forms.CharField(label="Member ID", max_length=20, widget=forms.TextInput(attrs={'class': 'border rounded p-2 w-full'}))

    def clean(self):
        cleaned_data = super().clean()
        isbn = cleaned_data.get('isbn')
        mem_id = cleaned_data.get('membership_id')

        # Check if book exists
        try:
            book = Book.objects.get(isbn=isbn)
            if book.available_copies < 1:
                raise forms.ValidationError("Book is currently unavailable.")
            cleaned_data['book_obj'] = book
        except Book.DoesNotExist:
            raise forms.ValidationError("Book with this ISBN not found.")

        # Check if member exists
        try:
            member = Member.objects.get(membership_id=mem_id)
            cleaned_data['member_obj'] = member
        except Member.DoesNotExist:
            raise forms.ValidationError("Member ID not found.")
            
        return cleaned_data

class MemberSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 outline-none'}))
    phone_number = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 outline-none'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 outline-none', 'rows': 3}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style the default Django fields to match our theme
        for field in self.fields:
            if 'class' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs['class'] = 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 outline-none'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Generate a random 8-character Membership ID
            mem_id = str(uuid.uuid4())[:8].upper()
            Member.objects.create(
                user=user,
                membership_id=mem_id,
                phone_number=self.cleaned_data['phone_number'],
                address=self.cleaned_data['address']
            )
        return user

# --- NEW FORM FOR DBMS MINI PROJECT (INSERT/UPDATE BOOKS) ---
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'genre', 'total_copies', 'available_copies', 'cover_image_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-2 border rounded mb-4 focus:ring-2 focus:ring-blue-500 outline-none'}),
            'author': forms.TextInput(attrs={'class': 'w-full p-2 border rounded mb-4 focus:ring-2 focus:ring-blue-500 outline-none'}),
            'isbn': forms.TextInput(attrs={'class': 'w-full p-2 border rounded mb-4 focus:ring-2 focus:ring-blue-500 outline-none'}),
            'genre': forms.TextInput(attrs={'class': 'w-full p-2 border rounded mb-4 focus:ring-2 focus:ring-blue-500 outline-none'}),
            'total_copies': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded mb-4 focus:ring-2 focus:ring-blue-500 outline-none'}),
            'available_copies': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded mb-4 focus:ring-2 focus:ring-blue-500 outline-none'}),
            'cover_image_url': forms.URLInput(attrs={'class': 'w-full p-2 border rounded mb-4 focus:ring-2 focus:ring-blue-500 outline-none', 'placeholder': 'https://example.com/image.jpg'}),
        }