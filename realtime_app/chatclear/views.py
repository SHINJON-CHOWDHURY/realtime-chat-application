

from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.views.decorators.http import require_POST

from django.contrib.auth import login
from django.contrib.auth.models import User

from django.db.models import Q

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .forms import (
    RegisterForm,
    EditProfileForm
)

from .models import (
    Message,
    UserProfile
)


# =========================
# REGISTER VIEW
# =========================
def register_view(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request,
    user,
    backend='django.contrib.auth.backends.ModelBackend')

            return redirect("home")

    else:

        form = RegisterForm()

    return render(
        request,
        "register.html",
        {
            "form": form
        }
    )


# =========================
# HOME VIEW
# =========================
@login_required
def home_view(request):

    query = request.GET.get("q")

    conversations = Message.objects.filter(
        Q(sender=request.user) |
        Q(receiver=request.user)
    ).order_by("-timestamp")

    user_last_message = {}

    for msg in conversations:

        # Skip unsent messages
        if msg.is_unsent:
            continue

        # Skip deleted messages
        if (
            msg.sender == request.user and
            msg.deleted_for_sender
        ):
            continue

        if (
            msg.receiver == request.user and
            msg.deleted_for_receiver
        ):
            continue

        other_user = (
            msg.receiver
            if msg.sender == request.user
            else msg.sender
        )

        if other_user.id not in user_last_message:

            user_last_message[
                other_user.id
            ] = msg.timestamp

    sorted_user_ids = list(
        user_last_message.keys()
    )

    previous_users = User.objects.filter(
        id__in=sorted_user_ids
    ).select_related(
        "userprofile"
    )

    previous_users = sorted(
        previous_users,
        key=lambda u:
            user_last_message[u.id],
        reverse=True
    )

    search_results = None

    if query:

        search_results = User.objects.filter(
            email__icontains=query
        ).exclude(
            id=request.user.id
        ).select_related(
            "userprofile"
        )

    return render(
        request,
        "home.html",
        {
            "previous_users": previous_users,
            "search_results": search_results
        }
    )


# =========================
# CHAT VIEW
# =========================
@login_required
def chat_view(request, user_id):

    other_user = get_object_or_404(
        User.objects.select_related(
            "userprofile"
        ),
        id=user_id
    )

    messages = Message.objects.filter(
        sender__in=[
            request.user,
            other_user
        ],
        receiver__in=[
            request.user,
            other_user
        ]
    ).order_by("timestamp")

    visible_messages = []

    for msg in messages:

        visible_messages.append(msg)

    return render(
        request,
        "chat.html",
        {
            "messages": visible_messages,
            "other_user": other_user
        }
    )


# =========================
# DELETE ENTIRE CHAT
# =========================
@login_required
@require_POST
def delete_chat_view(request, user_id):

    other_user = get_object_or_404(
        User,
        id=user_id
    )

    Message.objects.filter(
        sender__in=[
            request.user,
            other_user
        ],
        receiver__in=[
            request.user,
            other_user
        ]
    ).delete()

    return redirect("home")


# =========================
# REMOVE MESSAGE
# =========================
@login_required
@require_POST
def remove_message_view(request, msg_id):

    msg = get_object_or_404(
        Message,
        id=msg_id
    )

    if request.user == msg.sender:

        msg.deleted_for_sender = True

    elif request.user == msg.receiver:

        msg.deleted_for_receiver = True

    msg.save()

    # Realtime update
    ids = sorted([
        msg.sender.id,
        msg.receiver.id
    ])

    room_group_name = (
        f"chat_{ids[0]}_{ids[1]}"
    )

    channel_layer = get_channel_layer()

    async_to_sync(
        channel_layer.group_send
    )(
        room_group_name,
        {
            "type": "message_status_update",
            "message_id": msg.id,
            "status": "removed",
            "user_id": request.user.id,
        }
    )

    return redirect(
        request.META.get(
            "HTTP_REFERER",
            "home"
        )
    )


# =========================
# UNSEND MESSAGE
# =========================
@login_required
@require_POST
def unsend_message_view(request, msg_id):

    msg = get_object_or_404(
        Message,
        id=msg_id
    )

    # Only sender can unsend
    if msg.sender == request.user:

        msg.is_unsent = True

        msg.save()

    return redirect(
        request.META.get(
            "HTTP_REFERER",
            "home"
        )
    )


# =========================
# EDIT PROFILE
# =========================
@login_required
def edit_profile(request):

    profile, created = (
        UserProfile.objects.get_or_create(
            user=request.user
        )
    )

    if request.method == "POST":

        form = EditProfileForm(
            request.POST,
            request.FILES,
            instance=profile,
            user=request.user
        )

        if form.is_valid():

            request.user.username = (
                form.cleaned_data[
                    "username"
                ]
            )

            request.user.save()

            form.save()

            return redirect("home")

    else:

        form = EditProfileForm(
            instance=profile,
            user=request.user
        )

    return render(
        request,
        "edit_profile.html",
        {
            "form": form,
            "profile": profile
        }
    )