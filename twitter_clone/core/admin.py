from django.contrib import admin 
from .models import Account, Messages, Follow, FeedPost, Block, Chat


class AccountDisplay(admin.ModelAdmin):
	list_display = ('user', 'avatar_img', 'following', 'follower')
	#list_filter = (('admin', admin.RelatedOnlyFieldListFilter))
	def following(self, obj):
		return ", ".join(f.following.display_name for f in obj.following.all())

	def follower(self, obj):
		return ", ".join(f.follower.display_name for f in obj.follower.all())


class MessagesDisplay(admin.ModelAdmin):
	list_display = ('author', 'date')


class FollowerDisplay(admin.ModelAdmin):
	list_display = ('follower','following','followed_at')

class BlockDisplay(admin.ModelAdmin):
	list_display = ('blocker', 'blocking', 'blocked_since')
	
class FeedPostDisplay(admin.ModelAdmin):
	list_display = ('author','content','date')

class ChatDisplay(admin.ModelAdmin):
	list_display = ('chatter1', 'chatter2', 'created_chat_at')


admin.site.register(Chat, ChatDisplay)
admin.site.register(Account, AccountDisplay)
admin.site.register(Messages, MessagesDisplay)
admin.site.register(FeedPost, FeedPostDisplay)
admin.site.register(Follow, FollowerDisplay)
admin.site.register(Block, BlockDisplay)

