



from django.contrib import admin
from django.urls import path, include
from chatclear import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
path('accounts/', include('allauth.urls')),
    # Home
    path('', views.home_view, name='home'),

    # Chat
    path('chat/<int:user_id>/', views.chat_view, name='chat'),

    # Delete entire conversation
    path('chat/<int:user_id>/delete/', views.delete_chat_view, name='delete_chat'),

    # Message-level actions (NEW)
    path('message/<int:msg_id>/remove/', views.remove_message_view, name='remove_message'),
    path('message/<int:msg_id>/unsend/', views.unsend_message_view, name='unsend_message'),

    # Register
    path('register/', views.register_view, name='register'),

    # Login
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html'
    ), name='login'),

    # Logout
    path('logout/', auth_views.LogoutView.as_view(
        next_page='login'
    ), name='logout'),
]