import random
import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Transaction(models.Model):
    INCOME = 'income'
    EXPENSE = 'expense'

    TYPE_CHOICES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.FloatField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    @classmethod
    def generate_otp_for_user(cls, user):
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        code = f"{random.randint(100000, 999999)}"
        return cls.objects.create(user=user, otp=code)

    def is_valid(self):
        if self.is_used:
            return False
        return (timezone.now() - self.created_at) <= datetime.timedelta(minutes=10)

    def __str__(self):
        return f"PasswordResetOTP for {self.user.username}: {self.otp}"


class LoginOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_otps')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    @classmethod
    def generate_otp_for_user(cls, user):
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        code = f"{random.randint(100000, 999999)}"
        return cls.objects.create(user=user, otp=code)

    def is_valid(self):
        if self.is_used:
            return False
        return (timezone.now() - self.created_at) <= datetime.timedelta(minutes=10)

    def __str__(self):
        return f"LoginOTP for {self.user.username}: {self.otp}"