from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import transaction
import uuid

# Utility function
def generate_employee_code():
    return uuid.uuid4().hex[:10]  # Generate a unique 10-character employee code

# Custom User model
class CustomUser(AbstractUser):
    employee = models.OneToOneField(
        'Employee',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user'
    )

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username

# Employee model
class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    position = models.CharField(max_length=100)
    salary_rate = models.DecimalField(max_digits=10, decimal_places=2)
    hire_date = models.DateField()
    is_active = models.BooleanField(default=True)
    available_earnings = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Available balance for withdrawal"
    )
    employee_code = models.CharField(
        max_length=10, unique=True, default=generate_employee_code, blank=True
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.position}"

# PayoutRequest model
class PayoutRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processed', 'Processed')
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payout_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def process_request(self):
        """Processes the payout request and updates employee's available earnings."""
        with transaction.atomic():
            if self.status == 'Processed':
                raise ValueError("This payout request has already been processed.")

            if self.amount > self.employee.available_earnings:
                raise ValueError("Insufficient funds for this payout request.")

            self.employee.available_earnings -= self.amount
            self.employee.save()

            self.status = 'Processed'
            self.processed_at = timezone.now()
            self.save()

    def __str__(self):
        return f"Payout Request by {self.employee} for {self.amount} USD"
