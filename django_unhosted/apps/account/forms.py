#-*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django import forms

from oauth2app.models import AccessRange


class SignupForm(UserCreationForm):

	email = forms.EmailField(label='Email')


class LoginForm(forms.Form):

	username = forms.CharField(label='Username', max_length=30)
	password = forms.CharField(label='Password', widget=forms.PasswordInput)

	def clean(self):
		username = self.cleaned_data.get('username')
		password = self.cleaned_data.get('password')

		if username and password:
			self.user_cache = authenticate(username=username, password=password)
			if self.user_cache is None:
				raise forms.ValidationError( 'Please enter a correct username'
					' and password. Note that both fields are case-sensitive.')
			elif not self.user_cache.is_active:
				raise forms.ValidationError('This account is inactive.')
		return self.cleaned_data
