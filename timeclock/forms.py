from django import forms
from .models import Project

class PunchInForm(forms.Form):
    project = forms.ModelChoiceField(queryset = Project.objects.all())

class PunchOutForm(forms.Form):
    note = forms.CharField()

class PunchByDateForm(forms.Form):
    #projects = forms.ModelChoiceField(queryset = Project.objects.all())
    start_date = forms.DateField()
    end_date = forms.DateField()
