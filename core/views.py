from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth import authenticate, login


class IndexView(View):

    def get(self, *args, **kwargs):
        if self.request.user.is_anonymous:
            return redirect('core:login')
        return render(self.request, 'core/index.html')


class LoginView(View):
    
    def get(self, *args, **kwargs):
        return render(self.request, 'core/login.html')

    def post(self, *args, **kwargs):
        email = self.request.POST.get('email')
        password = self.request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user:
            login(self.request, user)
            messages.success(self.request, f'Welcome, {user.full_name}')
            return redirect('core:index')
        messages.error(self.request, 'Wrong email or password')
        return render(self.request, 'core/login.html', {
            'login_error': True,
        })