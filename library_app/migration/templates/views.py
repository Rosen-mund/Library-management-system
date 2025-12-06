from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Book, IssueTransaction
from .forms import BookSearchForm, IssueForm, ReturnForm


def login_view(request):
    if request.method == "POST":
        u = request.POST.get("username")
        p = request.POST.get("password")
        user = authenticate(request, username=u, password=p)
        if user:
            login(request, user)

            # Redirect based on role
            if user.is_staff:
                return redirect("admin_home")
            else:
                return redirect("user_home")

        messages.error(request, "Invalid credentials")
    return render(request, "library_app/login.html")



@login_required
def home(request):
    if request.user.is_staff:
        return redirect("admin_home")
    return redirect("user_home")


@login_required
def book_available(request):
    form = BookSearchForm(request.GET)
    books = Book.objects.all()

    if form.is_valid():
        if form.cleaned_data["title"]:
            books = books.filter(title__icontains=form.cleaned_data["title"])
        if form.cleaned_data["author"]:
            books = books.filter(author__icontains=form.cleaned_data["author"])
        if form.cleaned_data["serial_no"]:
            books = books.filter(serial_no__icontains=form.cleaned_data["serial_no"])

    return render(request, "library_app/book_available.html", {"books": books, "form": form})


@login_required
def book_issue(request, book_id=None):
    if request.method == "POST":
        form = IssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.user = request.user
            issue.status = "issued"

            issue.book.available = False
            issue.book.save()

            issue.save()
            messages.success(request, "Book issued successfully")
            return redirect("home")
    else:
        if book_id:
            book = get_object_or_404(Book, id=book_id)
            form = IssueForm(initial={
                "book": book,
                "serial_no": book.serial_no,
                "issue_date": timezone.now().date(),
                "expected_return_date": timezone.now().date() + timezone.timedelta(days=15),
            })
        else:
            form = IssueForm()

    return render(request, "library_app/book_issue.html", {"form": form})


@login_required
def return_book(request, trans_id):
    tx = get_object_or_404(IssueTransaction, id=trans_id)

    if request.method == "POST":
        form = ReturnForm(request.POST, instance=tx)
        if form.is_valid():
            tx.actual_return_date = form.cleaned_data["actual_return_date"]
            tx.status = "returned"
            tx.save()

            if tx.fine > 0 and not tx.fine_paid:
                return redirect("pay_fine", trans_id=tx.id)

            tx.book.available = True
            tx.book.save()

            messages.success(request, "Book returned successfully")
            return redirect("home")
    else:
        form = ReturnForm(instance=tx)

    return render(request, "library_app/return_book.html", {"form": form, "tx": tx})


@login_required
def pay_fine(request, trans_id):
    tx = get_object_or_404(IssueTransaction, id=trans_id)

    if request.method == "POST":
        tx.fine_paid = True
        tx.book.available = True
        tx.book.save()
        tx.save()

        messages.success(request, "Fine paid successfully")
        return redirect("home")

    return render(request, "library_app/pay_fine.html", {"tx": tx})


@login_required
def reports(request):
    issued = IssueTransaction.objects.filter(status="issued")
    returned = IssueTransaction.objects.filter(status="returned")
    return render(request, "library_app/reports.html", {"issued": issued, "returned": returned})

@login_required
def admin_home(request):
    return render(request, "library_app/admin_home.html")

@login_required
def user_home(request):
    return render(request, "library_app/user_home.html")
