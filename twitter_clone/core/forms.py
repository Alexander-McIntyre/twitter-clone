from django import forms 
from django.core.exceptions import ValidationError 
from django.contrib.auth import authenticate 
from core.models import Follow, Block
import re


class LoginForm(forms.Form):
	username = forms.CharField(max_length=100, required=True)
	password = forms.CharField(label='Password', max_length=100, required=True, widget=forms.PasswordInput)
	
	def clean(self):
		cleaned_data=super().clean()
		user = authenticate(
			username = cleaned_data.get('username'),
			password = cleaned_data.get('password'))
		if user is None:
			self.errors['username'] = self.error_class(['You Sure'])
			self.errors['password'] = self.error_class(['WRONG WRONG WRONG'])
			raise ValidationError('User doesn\'t exist. Or details entered incorrectly')
		return self.cleaned_data


class UserForm(forms.Form):
	display_name = forms.CharField(label='Display Name', max_length=100, required=True)
	username = forms.CharField(label='Username', max_length =100, required=True)
	password = forms.CharField(widget=forms.PasswordInput, label='Password', max_length=100, required=True)
	avatar = forms.FileField(label='Avatar', required=True)
	
	def clean(self): 
		display_name_regex = r'[A-Za-z -]'
		user_regex = r'[A-za-z0-9@#.]'
		cleaned_data = super().clean()
		display_name = cleaned_data.get('display_name')
		username = cleaned_data.get('username')
		password = cleaned_data.get('password')
		if len(password) < 8:
			self._errors['password'] = self.error_class([' must be longer than 8 characters'])
		'''
		if not re.match(display_name_regex, display_name):
			self._errors['display_name'] = self.error_class(['Wrong format, see below'])
		if not re.match(user_regex, username):
			self._errors['username'] = self.error_class(['Wrong format, see below'])
		'''
		return self.cleaned_data	
	
class FeedPostForm(forms.Form):
	feedpost = forms.CharField(max_length=400, required=True)

	def clean(self):
		cleaned_data = super().clean()
		feedpost = cleaned_data.get('feedpost')
		

class FollowForm(forms.Form):
	def __init__(self, *args, follower=None, following=None, **kwargs):
		super().__init__(*args,**kwargs)
		self.follower = follower
		self.following = following


	def clean(self):
		if self.follower == self.following:
			raise forms.ValidationError("can't follow yourself")
		if Follow.objects.filter(follower=self.follower, following=self.following).exists():
			raise forms.ValidationError("You already follow this person")
		if Block.objects.filter(blocker=self.follower, blocking=self.following).exists():
			raise forms.ValidationError('This user has blocked you')
		return super().clean()
	def save(self):
		Block.objects.filter(blocker=self.follower, blocking=self.following).delete()
		return Follow.objects.create(
				follower=self.follower,
				following=self.following
				)


class BlockForm(forms.Form):
	def __init__(self, *args, blocker=None, blocking=None, **kwargs):
		super().__init__(*args,**kwargs)
		self.blocker = blocker 
		self.blocking = blocking 


	def clean(self):
		if self.blocker == self.blocking:
			raise ValidationError("can't block yourself")
		if Block.objects.filter(blocker=self.blocker, blocking=self.blocking).exists():
			raise ValidationError("you already block this person")
		return super().clean()

	def save(self):
		Follow.objects.filter(follower=self.blocker, following=self.blocking).delete()
		Follow.objects.filter(follower=self.blocking, following=self.blocker).delete()
		return Block.objects.create(
				blocker=self.blocker,
				blocking=self.blocking
				)
