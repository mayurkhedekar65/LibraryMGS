from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# --- MEMBER MODEL ---
class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member_profile')
    membership_id = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.membership_id})"

# --- BOOK MODEL ---
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    genre = models.CharField(max_length=100)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    cover_image_url = models.URLField(blank=True, null=True) # Store image link
    
    def __str__(self):
        return self.title

# --- TRANSACTION MODEL ---
class Transaction(models.Model):
    STATUS_CHOICES = (
        ('Issued', 'Issued'),
        ('Returned', 'Returned'),
    )

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    
    issue_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateTimeField()
    actual_return_date = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Issued')
    fine_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        # Auto-set expected return date to 14 days from now if not set
        if not self.id and not self.expected_return_date:
            self.expected_return_date = timezone.now() + timezone.timedelta(days=14)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} - {self.member.user.username}"