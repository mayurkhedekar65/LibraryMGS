from django.contrib import admin
from .models import Member, Book, Transaction

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'available_copies', 'total_copies')
    search_fields = ('title', 'isbn')

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'membership_id', 'phone_number')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('book', 'member', 'issue_date', 'status', 'fine_amount')
    list_filter = ('status', 'issue_date')