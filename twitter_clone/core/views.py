from django.shortcuts import render, redirect, get_object_or_404 
from django.http import HttpResponse, JsonResponse 
from django.views.decorators.csrf import csrf_exempt 
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.models import User 
from django.template.loader import render_to_string 
from django.shortcuts import render, redirect 
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger 
from django.conf import settings 
from core.forms import LoginForm, UserForm, FeedPostForm, FollowForm, BlockForm
from core.models import Account, Messages, FeedPost, Follow, Block, Chat
import json, sys


def home(request):
	login_form = LoginForm()
	registration_form = UserForm()
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		if request.FILES:
			login_form = LoginForm()
			registration_form = UserForm(request.POST, request.FILES)
			form = registration_form
		else:
			login_form = LoginForm(request.POST)
			registration_form = UserForm()
			form = login_form
		if form.is_valid():
			user = authenticate(request, username=username, password=password)
			if user is not None:
				login(request,user)
	if request.user.is_authenticated:
		return redirect('feed')
	else: 
		return render(request, 'home.html', {'login_form': login_form, 'registration_form': registration_form})


def registration(request):
	if request.method == 'POST':
		form = UserForm(request.POST, request.FILES)
		if form.is_valid():
			new_usr = User.objects.create_user(username=request.POST.get('username'), password=request.POST.get("password"))
			login(request, new_usr)
			new_account = Account(
					display_name=request.POST.get("display_name"),
					user=new_usr,
					avatar_img=request.FILES['avatar']
					)
			new_account.save()
			return redirect('feed')
	return render(request, 'home.html', {'login_form': LoginForm(), 'registration_form': UserForm()})


def log_out(request):
	logout(request)
	return redirect('/', {'login_form': LoginForm(), 'registration_form': UserForm()})


def profile(request, display_name):
	account = get_object_or_404(Account, display_name=display_name)
	posts = FeedPost.objects.filter(author=request.user.account)
	posts = FeedPost.objects.filter(author=account)
	return render(request, 'profile.html', {'account': account, 'posts': posts})


def profile_update(request):
	return


def feed(request):
	if request.method == 'POST':
		form=FeedPostForm(request.POST)
		if form.is_valid():
			FeedPost.objects.create(
				content=form.cleaned_data['feedpost'],
				author=request.user.account
				)
			return redirect('feed')
	else:
		form=FeedPostForm()
	following_users = list(Follow.objects.filter(follower=request.user.account).values_list('following', flat=True)) + [request.user.account.id]
	posts = FeedPost.objects.filter(author__in=following_users).order_by('-date')
	mult = 1 #TODO make possible from html/js
	#mult = int(request.GET.get('mult'))
	posts_to_display = 20 #TODO user mutable, add as env varibale in settings.py till then 
	posts_to_paginate = [post for post in posts]
	paginator = Paginator(posts_to_paginate[:posts_to_display*mult], posts_to_display)

	if len(posts) <= posts_to_display:
		return render(request, 'feed.html', {'form': form, 'posts': posts})
	else:
		return render(request, 'feed.html', {'form': form, 'posts': posts}) #TODO pagination 


def follow_or_block(request, display_name, follow_or_block):
	following_or_blocking = get_object_or_404(Account, display_name=display_name)
	current_user = request.user.account
	if request.method == 'POST':
		if follow_or_block == 'block':
			form = BlockForm(request.POST, blocker=current_user, blocking=following_or_blocking )	
		else:
			form = FollowForm(request.POST, follower=current_user, following=following_or_blocking )
		if form.is_valid():
			form.save()
		else:
			which_form_error = f'{follow_or_block}_form'
			return render(request, 'profile.html', {which_form_error:form, 'account':following_or_blocking })
	return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def chat(request, other_chatter_id):
	current_chatter = request.user.account
	other_chatter = Account.objects.get(id=other_chatter_id)
	other_chatter_avi = other_chatter.avatar_img
	if other_chatter.id > current_chatter.id:
		chatter1, chatter2 = other_chatter, current_chatter
	else:
		chatter1, chatter2 = current_chatter, other_chatter 
	if not Chat.objects.filter(chatter1=chatter1, chatter2=chatter2).exists():
		chat = Chat.objects.create(chatter1=chatter1, chatter2=chatter2)
	else:
		chat=Chat.objects.get(chatter1=chatter1, chatter2=chatter2)
	return render(request, 'chat.html', {'chat': chat, 'chat_id':chat.id, 'other_chatter_avi':other_chatter_avi})


@csrf_exempt
@login_required
def send_msg(request):
	if request.method == 'POST':
		data = json.loads(request.body)
		message = data.get('message')
		author=Account.objects.get(display_name=data.get('author'))
		tmp = 0
		while tmp<10:
			try: 
				message = Messages.objects.filter(author=author.id, context=message).order_by('-date').first()
				break
			except Exception as e:
				print(e)
				tmp+=1
		data = render_to_string('messages.html', {'message': message, 'requested_user': request.user.account})
		return HttpResponse(data)


@login_required
def get_msg(request, pk):
	msg_to_pag = []
	chat = Chat.objects.get(id=pk)
	msg_display=settings.CHAT_MESSAGE_NUMBER_DEFAULT
	message_lst = Messages.objects.filter(room=chat).order_by('date').distinct()
	mult = int(request.GET.get('mult'))
	if len(message_lst) == 0:
		return render(request, 'chat.html', {'chat': chat, 'message_lst': message_lst})
	for message in message_lst:
		msg_to_pag.append(message)
	paginator = Paginator(msg_to_pag[-msg_display*mult:], msg_display)
	if (mult * msg_display) > len(msg_to_pag):
		if (len(msg_to_pag) % msg_display == 0) or (mult*msg_display > len(msg_to_pag)+msg_display):
			sys.exit()
		else:
			paginator = Paginator(msg_to_pag[-msg_display * mult:], len(msg_to_pag)-((mult-1)*msg_display))
	page = request.GET.get('page',1)
	messages = paginator.page(page)
	data = render_to_string('get_msg.html', {'messages': messages, 'requested_user': request.user.account})
	return JsonResponse(data, safe=False)
