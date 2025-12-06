from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path("", lambda request: redirect("login"), name="root"),
    path("login/", views.login_view, name="login"),
    path("home/", views.home, name="home"),
    path("books/", views.book_available, name="books"),
    path("issue/<int:book_id>/", views.book_issue, name="book_issue"),
    path("return/<int:trans_id>/", views.return_book, name="return_book"),
    path("payfine/<int:trans_id>/", views.pay_fine, name="pay_fine"),
    path("reports/", views.reports, name="reports"),
    path("admin_home/", views.admin_home, name="admin_home"),
    path("user_home/", views.user_home, name="user_home"),
]

