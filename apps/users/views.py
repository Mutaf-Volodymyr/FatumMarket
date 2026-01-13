from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import LoginForm, SignupForm
from .backends import PhoneOrEmailBackend


def login_view(request):
    """Вход пользователя"""
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login_value = form.cleaned_data['login']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=login_value, password=password)
            if user:
                login(request, user, backend='apps.users.backends.PhoneOrEmailBackend')
                next_url = request.GET.get('next', '/')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверный email/телефон или пароль')
    else:
        form = LoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    """Выход пользователя"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('/')


def signup_view(request):
    """Регистрация нового пользователя"""
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='apps.users.backends.PhoneOrEmailBackend')
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('/')
    else:
        form = SignupForm()
    
    return render(request, 'auth/signup.html', {'form': form})

