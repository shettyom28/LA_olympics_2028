import logging
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect

from .models import UserProfile, Country, Event, Message
from .forms import RegistrationForm, LoginForm, EditUserProfileForm, ExampleMessageForm

logger = logging.getLogger(__name__)

def index(request: HttpRequest):
    events = Event.objects.select_related('sport', 'venue').all()[:5]
    messages = Message.objects.select_related('user').all().order_by('-created_at')[:10]
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = ExampleMessageForm(request.POST)
        if form.is_valid():
            msg = Message.objects.create(
                user=request.user,
                content=form.cleaned_data['content']
            )
            from .service_pub import publish_example_message
            publish_example_message(msg.id, msg.content, msg.user.username)
            return redirect('myapp:index')
    else:
        form = ExampleMessageForm()
        
    return render(request, 'myapp/index.html', {
        'events': events,
        'board_messages': messages,
        'form': form
    })

def user_registration(request: HttpRequest):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            role = form.cleaned_data.get('role', 'spectator')
            UserProfile.objects.create(
                user=user,
                role=role,
                country=form.cleaned_data.get('country')
            )
            # Sync with Django Groups
            from django.contrib.auth.models import Group
            group, _ = Group.objects.get_or_create(name=role.capitalize())
            user.groups.add(group)
            
            return redirect('myapp:login')
    else:
        form = RegistrationForm()
    return render(request, 'myapp/register.html', {'form': form})

def user_login(request: HttpRequest):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request, 
                username=form.cleaned_data['username'], 
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                return redirect('myapp:index')
            else:
                form.add_error(None, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'myapp/login.html', {'form': form})

@login_required
def user_logout(request: HttpRequest):
    logout(request)
    return redirect('myapp:index')

@login_required
def profile_edit(request: HttpRequest):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = EditUserProfileForm(request.POST)
        if form.is_valid():
            old_role = user_profile.role
            user_profile.role = form.cleaned_data.get('role', user_profile.role)
            user_profile.country = form.cleaned_data.get('country', user_profile.country)
            user_profile.save()
            
            # Sync with Django Groups
            if user_profile.role != old_role:
                from django.contrib.auth.models import Group
                # Remove from old group
                old_group = Group.objects.filter(name=old_role.capitalize()).first()
                if old_group:
                    request.user.groups.remove(old_group)
                # Add to new group
                new_group, _ = Group.objects.get_or_create(name=user_profile.role.capitalize())
                request.user.groups.add(new_group)
                
            return redirect('myapp:profile_edit')
    else:
        initial = {
            'role': user_profile.role,
            'country': user_profile.country,
        }
        form = EditUserProfileForm(initial=initial)
    return render(request, 'myapp/profile_edit.html', {'form': form})

def profile_detail(request: HttpRequest, username: str):
    target_user = get_object_or_404(User, username=username)
    return render(request, 'myapp/profile_detail.html', {'target_user': target_user})