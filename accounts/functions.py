# accounts/functions.py

from main.models import Template
from django.core.mail import send_mail

# when a new user registers, make a copy of all the "for_all" templates for the new user's account
def create_user_templates(user):
	available_temps = Template.objects.filter(for_all=True)
	for temp in available_temps:
		new_temp = Template(user=user, name="temporary")
		new_temp.save()
		new_temp.copy(to_copy=temp)

# send an email notification when a new user registers
def send_new_user(user):
	send_mail(
		subject="New User", 
		message=f"A new user {user.email} joined.", 
		from_email=user.email,
		recipient_list=['myemsnarrative@gmail.com'], 
		fail_silently=False
		)

	return True
