from django import forms

class SearchForm(forms.Form):
	job_title = forms.CharField(max_length=100)
	skills = forms.CharField(max_length=100)
	location = forms.CharField(max_length=50)
	