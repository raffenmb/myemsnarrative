from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate

from accounts.models import CustomUser

class RegistrationForm(UserCreationForm):
	email = forms.EmailField(max_length=60)
	username = forms.CharField(max_length=60)

	class Meta:
		model = CustomUser
		fields = ('email', 'username', 'password1', 'password2')

class AccountAuthenticationForm(forms.ModelForm):
	password = forms.CharField(label = 'Password', widget=forms.PasswordInput)

	class Meta: 
		model = CustomUser
		fields = ('email', 'password')

	def clean(self):
		if self.is_valid():
			email = self.cleaned_data['email']
			password = self.cleaned_data['password']
			if not authenticate(email=email, password=password):
				raise forms.ValidationError('Invalid login')

class AccountUpdateForm(forms.ModelForm):

	class Meta:
		model = CustomUser
		fields = ('username', 'email', 'department')

	def clean_email(self):
		email = self.cleaned_data['email'].lower()
		try:
			account = CustomUser.objects.exclude(pk=self.instance.pk).get(email=email)
		except CustomUser.DoesNotExist:
			return email
		raise forms.ValidationError(f'Email {email} is already in use')

	def clean_username(self):
		username = self.cleaned_data['username']
		try:
			account = CustomUser.objects.exclude(pk=self.instance.pk).get(username=username)
		except CustomUser.DoesNotExist:
			return username
		raise forms.ValidationError(f'Username {username} is already in use.')

	def save(self, commit=True):
		account = super(AccountUpdateForm, self).save(commit=False)
		account.username = self.cleaned_data['username']
		account.email = self.cleaned_data['email']
		if commit:
			account.save()
		return account