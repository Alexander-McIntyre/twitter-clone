from django.urls import path
from . import views

urlpatterns = [
	path("", views.home, name="home"),
	path('login/', views.login, name='login'),

	path('log_out/', views.log_out, name='log_out'),
	path('user/profile_update/', views.profile_update, name='profile_update'),
	path('registration/', views.registration, name='registration'),
	path('feed/', views.feed, name='feed'),
	path('profile/<str:display_name>/', views.profile, name='profile'),
	path('follow/<str:display_name>/<str:follow_or_block>', views.follow_or_block, name='follow_or_block'),

	path('chat/<int:other_chatter_id>/', views.chat, name='chat'),
	path('send_msg/', views.send_msg, name='send_msg'),
	path('get_msg/<int:pk>/', views.get_msg, name='get_msg'),
]

