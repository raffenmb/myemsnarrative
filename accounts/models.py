from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class CustomUserManager(BaseUserManager):
	# instructions when creating a regular user
	def create_user(self, email, username, password, **other_fields):
		if not email:
			raise ValueError(_("You must provide an email address"))
		if not username:
			raise ValueError(_("You must provide a username"))

		email = self.normalize_email(email)
		user = self.model(email=email, username=username, **other_fields)
		user.set_password(password)
		user.save()
		return user

	# instructions when creating a superuser
	def create_superuser(self, email, username, password, **other_fields):
		user = self.create_user(
			email=self.normalize_email(email),
			password=password,
			username=username,
		)
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save()
		return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
	email = models.EmailField(_('email address'), unique=True)
	username = models.CharField(max_length=150, unique=True)
	date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
	last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
	is_admin = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	is_superuser = models.BooleanField(default=False)
	is_temp_user = models.BooleanField(default=False)
	agreed_to_policy = models.BooleanField(default=False)
	department = models.CharField(max_length=255, null=True, blank=True)

	# set the username to email as opposed to username, but make username a required field
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username',]

	objects = CustomUserManager()

	def __str__(self):
		return self.username

	def has_perm(self, perm, obj=None):
		return self.is_admin

	def has_module_perms(self, app_label):
		return True