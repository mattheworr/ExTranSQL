from django import forms

class FileForm(forms.Form):
    email = forms.CharField(label='Email: ')
    raw_file = forms.FileField(label='File: ')