from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Account(models.Model):
	display_name = models.CharField(max_length=40)
	user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
	avatar_img = models.ImageField(upload_to='account_avi', null=False, blank=False)

	def save(self, *args, **kwargs):
		super(Account, self).save(*args, **kwargs)

	def __str__(self):
		return self.display_name


class FeedPost(models.Model):
	content = models.CharField(max_length=150)
	author = models.ForeignKey(Account, related_name='feed_post', on_delete=models.CASCADE)
	date = models.DateTimeField(default=timezone.now)
	
	def __str__(self):
		return self.author.user.username


class Follow(models.Model):
	following = models.ForeignKey(Account, related_name='follower', on_delete=models.CASCADE)
	follower = models.ForeignKey(Account, related_name='following', on_delete=models.CASCADE)
	followed_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-followed_at']


class Block(models.Model):
	blocker = models.ForeignKey(Account, related_name='blocking', on_delete=models.CASCADE)
	blocking = models.ForeignKey(Account, related_name='blocker', on_delete=models.CASCADE)
	blocked_since = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		unique_together = ('blocker', 'blocking')


class Chat(models.Model):
	chatter1 = models.ForeignKey(Account, related_name='chatter1', on_delete=models.CASCADE)
	chatter2 = models.ForeignKey(Account, related_name='chatter2', on_delete=models.CASCADE)
	created_chat_at = models.DateTimeField(auto_now_add=True)

	def save(self, *args, **kwargs):
		#if self.chatter1.id > self.chatter2.id:
		#	self.chatter1, self.chatter2 = self.chatter2, self.chatter1
		super().save(*args, **kwargs)


class Messages(models.Model):
	room = models.ForeignKey(Chat, related_name='chat', on_delete=models.CASCADE, null=True)
	author = models.ForeignKey(Account, related_name='messages', on_delete=models.CASCADE)
	context = models.TextField()
	date = models.DateTimeField(default='timezone.now')

	def __str__(self):
		return self.author.user.username

	class Meta:
		verbose_name = 'Message'
		verbose_name_plural = 'Messages'
