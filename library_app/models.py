from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    serial_no = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=20, choices=(("book","Book"), ("movie","Movie")))
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    membership_no = models.CharField(max_length=20, unique=True)
    duration_months = models.IntegerField(default=6)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=self.duration_months * 30)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.membership_no


class IssueTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    serial_no = models.CharField(max_length=50)
    issue_date = models.DateField(default=timezone.now)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True)
    fine = models.IntegerField(default=0)
    fine_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=(("issued","Issued"),("returned","Returned")), default="issued")

    def save(self, *args, **kwargs):
        if not self.expected_return_date:
            self.expected_return_date = self.issue_date + timedelta(days=15)

        if self.status == "returned" and self.actual_return_date:
            diff = (self.actual_return_date - self.expected_return_date).days
            self.fine = max(0, diff * 10)
            if self.fine == 0:
                self.fine_paid = True

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} ({self.user.username})"
