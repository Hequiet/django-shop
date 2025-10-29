from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import (get_cookie_view,
                    set_cookie_view,
                    set_session_view,
                    get_session_view,
                    AboutMeView,
                    RegisterView,
                    FooBarView,
                    ProfileUpdateView,
                    AvatarUpdateView,
                    UserListView,
                    user_detail_view,
                    HelloView,
                    )

app_name = "myauth"
urlpatterns = [
    path("login/", LoginView.as_view(
        template_name="myauth/login.html",
        redirect_authenticated_user=True,
    ),
         name="login"),
    path("logout/", LogoutView.as_view(next_page="myauth:login"),
         name="logout"),
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("user/<int:pk>", user_detail_view, name="user_detail"),
    path("update-profile/", ProfileUpdateView.as_view(), name="update-profile"),
    path("update-profile/<int:pk>", AvatarUpdateView.as_view(), name="profile_update_other"),
    path("register/", RegisterView.as_view(), name="register"),
    path('user_list/', UserListView.as_view(), name='user_list'),
    path('cookie/get/', get_cookie_view, name='cookie_get'),
    path('cookie/set/', set_cookie_view, name='cookie_set'),
    path('session/get/', get_session_view, name='session_get'),
    path('session/set/', set_session_view, name='session_set'),
    path('foo-bar/', FooBarView.as_view(), name='foo_bar'),
    path('hello/', HelloView.as_view(), name='hello'),
]
