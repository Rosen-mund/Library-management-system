from django import forms
from .models import IssueTransaction
from django.utils import timezone

class BookSearchForm(forms.Form):
    title = forms.CharField(required=False)
    author = forms.CharField(required=False)
    serial_no = forms.CharField(required=False)


class IssueForm(forms.ModelForm):
    class Meta:
        model = IssueTransaction
        fields = ["book", "serial_no", "issue_date", "expected_return_date", "remarks"]

    def clean_issue_date(self):
        d = self.cleaned_data["issue_date"]
        if d < timezone.now().date():
            raise forms.ValidationError("Issue date cannot be in the past.")
        return d

    def clean_expected_return_date(self):
        i = self.cleaned_data["issue_date"]
        r = self.cleaned_data["expected_return_date"]

        if (r - i).days > 15:
            raise forms.ValidationError("Return date cannot exceed 15 days.")
        return r


class ReturnForm(forms.ModelForm):
    class Meta:
        model = IssueTransaction
        fields = ["actual_return_date", "remarks"]
