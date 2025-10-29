from itertools import product

from random import random
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.urls import reverse, reverse_lazy
from django.views.generic import View, TemplateView, CreateView, UpdateView, ListView
from django.utils.translation import gettext_lazy as _,ngettext
from django.views.decorators.cache import cache_page

from .forms import UserAndProfileForm
from .models import Profile


class HelloView(View):
    welcome_massage = _("welcome hello world")
    def get(self, request):
        items_str = request.GET.get('items') or 0
        items = int(items_str)
        products_line = ngettext("one product",
                                 "{count} products", items)
        products_line = products_line.format(count=items)
        return HttpResponse(f"<h1>{self.welcome_massage}</h1>"
                            f"<h2>{products_line}</h2>")



class AboutMeView(UpdateView):
    model = Profile
    fields = ['avatar']
    template_name = 'myauth/about-me.html'
    success_url = '/accounts/about-me/'

    def get_object(self, queryset=None):
        return self.request.user.profile if self.request.user.is_authenticated else None


def user_detail_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'myauth/user_detail.html', {'user': user})


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'myauth/register.html'
    success_url = reverse_lazy('myauth:about-me')

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(self.request,
                            username=username,
                            password=password)
        login(self.request, user)
        return response


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/admin/')
        return render(request, 'myauth/login.html')

    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('/admin/')
    return render(request, 'myauth/login.html', {'error': 'Invalid username or password.'})


def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse('Cookies set')
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response


@cache_page(10)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f'Cookie value:{value} + {random()}')


def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse('Session set')


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default value")
    return HttpResponse(f'Session value {value}')


class FooBarView(View):
    def get(self, request) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})


class AvatarUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Profile
    fields = ['avatar', ]
    template_name_suffix = "_update_form"

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Profile, user_id=pk)

    def test_func(self):
        pk = self.kwargs.get('pk')
        return self.request.user.is_staff

    def get_success_url(self):
        pk = self.kwargs.get('pk')
        return reverse('myauth:user_detail', kwargs={'pk': pk})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = UserAndProfileForm
    template_name_suffix = "_update_form"

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_success_url(self):
        return reverse('myauth:about-me')


class UserListView(LoginRequiredMixin, ListView):
    template_name = 'myauth/profile_user_list.html'
    queryset = User.objects.all()
    context_object_name = 'users'
