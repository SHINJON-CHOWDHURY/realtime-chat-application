from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include

from chatclear import views

from django.contrib.auth import views as auth_views


urlpatterns = [

    path('admin/', admin.site.urls),

    path(
        'accounts/',
        include('allauth.urls')
    ),

    # HOME
    path(
        '',
        views.home_view,
        name='home'
    ),

    # CHAT
    path(
        'chat/<int:user_id>/',
        views.chat_view,
        name='chat'
    ),

    # DELETE CHAT
    path(
        'chat/<int:user_id>/delete/',
        views.delete_chat_view,
        name='delete_chat'
    ),

    # MESSAGE ACTIONS
    path(
        'message/<int:msg_id>/remove/',
        views.remove_message_view,
        name='remove_message'
    ),

    path(
        'message/<int:msg_id>/unsend/',
        views.unsend_message_view,
        name='unsend_message'
    ),

    # REGISTER
    path(
        'register/',
        views.register_view,
        name='register'
    ),

    # EDIT PROFILE
    path(
        'edit-profile/',
        views.edit_profile,
        name='edit_profile'
    ),

    # LOGIN
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='login.html'
        ),
        name='login'
    ),

    # LOGOUT
    path(
        'logout/',
        auth_views.LogoutView.as_view(
            next_page='login'
        ),
        name='logout'
    ),
]


# MEDIA FILES
if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )