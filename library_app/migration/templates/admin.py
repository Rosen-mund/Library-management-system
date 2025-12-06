from django.contrib import admin
from .models import Book, Membership, IssueTransaction

admin.site.register(Book)
admin.site.register(Membership)
admin.site.register(IssueTransaction)
