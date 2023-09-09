# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
import json

from accounts.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
from django.contrib import messages
from accounts.models import CustomUser
from accounts import functions as fx

# change's the user's password from the account page
@login_required
def change_password_view(request):
	if request.method == "POST":
		form = PasswordChangeForm(request.user , request.POST)
		if form.is_valid():
			user = form.save
			update_session_auth_hash(request , user)
			messages.success(request , "Your password was successfully updated")
			return redirect('accounts:user_account')
		else:
			print("form not valid")
			# return redirect('accounts:change_password')
	else:
		form  = PasswordChangeForm(request.user)

	context = {
		'owner': request.user,
		'form': form,
		}

	return render(request, 'accounts/change_password.html', context)


def email_sent_view(request):
	context = {}

	return render(request, 'accounts/email_sent.html', context)

# logs the user in
def login_view(request):
	user = request.user
	error_message = None

	if user.is_authenticated:
		return redirect('main:home')

	if request.POST:
		form = AccountAuthenticationForm(request.POST)
		if form.is_valid():
			user = authenticate(
				email = form.cleaned_data['email'],
				password = form.cleaned_data['password'],
			)

			if user is not None:
				login(request, user)
				return redirect('main:acknowledgment')
		else:
			form_errors = json.loads(form.errors.as_json())
			if form_errors:
				for error_type, error in form_errors.items():
					error_message = error[0]["message"]
					break
	else:
		form = AccountAuthenticationForm()

	context = {
		'form': form,
		'error_message': error_message,
	}

	return render(request, 'accounts/login.html', context)

# logs the user out
def logout_view(request):
	logout(request)
	return redirect('main:welcome')

# automatically sent here from password reset on unauthorized side, so just redirecting for one less html
def password_reset_complete_view(request):
	messages.success(request , "Your password has been successfully updated")
	return redirect ("accounts:login")

def password_reset_view(request):
	error_message = None
	if request.POST:
		form = PasswordResetForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data['email']
			associated_users = CustomUser.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "accounts/password_reset_email.txt"
					email_context = {
						"email": user.email,
						'domain':'myemsnarrative.com',
						'site_name': 'My EMS Narrative',
						"uid": urlsafe_base64_encode(force_bytes(user.pk)),
						"user": user,
						'token': default_token_generator.make_token(user),
						'protocol': 'https',
					}
					email = render_to_string(email_template_name, email_context)
					try:
						send_mail(subject, email, 'myemsnarrative@gmail.com' , [user.email], fail_silently=False)
					except:
						pass
					messages.success(request , "Instructions have been sent to your email")
					return redirect ("accounts:login")
			else:
				error_message = "There is no account with that email address"
	else:
		form = PasswordResetForm()

	context = {
		'form': form,
		'error_message': error_message,
	}

	return render(request, "accounts/password_reset.html", context)

# register a new user
def register_view(request):
	error_message = None

	if request.POST:
		form = RegistrationForm(request.POST)
		if form.is_valid():
			form.save()
			email = form.cleaned_data.get('email')
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(email=email, password=raw_password)
			login(request, user)
			# add templates to user's db
			fx.create_user_templates(user=user)
			# send email to admin to alert there is a new user
			fx.send_new_user(user=user)
			return redirect('main:acknowledgment')
		else:
			form_errors = json.loads(form.errors.as_json())
			if form_errors:
				for error_type, error in form_errors.items():
					error_message = error[0]["message"]
					break
	else:
		form = RegistrationForm()

	context = {
		"form": form,
		"error_message": error_message,
	}

	return render(request, 'accounts/register.html', context)


@login_required
def user_account_view(request):
	update_error = False
	if request.POST:
		post = request.POST

		form = AccountUpdateForm(post, instance=request.user)
		if form.is_valid():
			form.save()
			return redirect("accounts:user_account")
		else:
			update_error = True
			form = AccountUpdateForm(post, instance=request.user,
				initial = {
					"email": request.user.email,
					"username": request.user.username,
					"department": request.user.department,
				}
			)
	else: 
		form = AccountUpdateForm(
			initial = {
				"email": request.user.email,
				"username": request.user.username,
				"department": request.user.department,
			}
		)	

	context = {
		'owner': request.user,
		'form': form,
		'update_error': update_error,
		}

	return render(request, 'accounts/user_account.html', context)
