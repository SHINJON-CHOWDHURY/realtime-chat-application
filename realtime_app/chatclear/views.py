import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from django.http import JsonResponse
from .ai.services import ask_ai
from django.views.decorators.csrf import csrf_exempt
from .ai.services import ask_ai
from .models import AIConversation

from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.http import JsonResponse

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
    UserProfile,
    AIConversation
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

    # =========================
    # AI CONVERSATIONS
    # =========================

    ai_conversations = AIConversation.objects.filter(
        user=request.user
    ).order_by("timestamp")

    return render(
        request,
        "home.html",
        {
            "previous_users": previous_users,
            "search_results": search_results,
            "ai_conversations": ai_conversations,
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

    visible_messages = list(messages)

    # Retrieve the current user's saved AI conversations.
    ai_conversations = list(
        AIConversation.objects.filter(
            user=request.user
        ).order_by("timestamp")
    )

    # Combine normal messages and AI interactions into one chronological timeline.
    conversation_timeline = []

    for msg in visible_messages:
        conversation_timeline.append({
            "type": "message",
            "timestamp": msg.timestamp,
            "message": msg,
        })

    for ai in ai_conversations:
        conversation_timeline.append({
            "type": "ai",
            "timestamp": ai.timestamp,
            "ai": ai,
        })

    conversation_timeline.sort(key=lambda entry: entry["timestamp"])

    return render(
        request,
        "chat.html",
        {
            "messages": visible_messages,
            "other_user": other_user,
            "ai_conversations": ai_conversations,
            "conversation_timeline": conversation_timeline,
        }
    )
# =========================
# FILE UPLOAD
# =========================
@login_required
@require_POST
def upload_file_view(request, user_id):

    # Get receiver
    other_user = get_object_or_404(
        User,
        id=user_id
    )

    # Get uploaded file
    uploaded_file = request.FILES.get("file")

    # Optional caption
    content = request.POST.get(
        "content",
        ""
    ).strip()

    # Make sure file exists
    if not uploaded_file:
        return JsonResponse(
            {
                "success": False,
                "error": "No file was uploaded."
            },
            status=400
        )

    # Save message
    message = Message.objects.create(
        sender=request.user,
        receiver=other_user,
        content=content,
        attachment=uploaded_file,
        attachment_name=uploaded_file.name,
        attachment_type=(
            uploaded_file.content_type
            or ""
        ),
        attachment_size=uploaded_file.size
    )

    # =====================================
    # REAL-TIME FILE MESSAGE
    # =====================================

    ids = sorted([
        request.user.id,
        other_user.id
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
    "type": "file_message",

    "message_id": message.id,

    "sender": request.user.username,

    "sender_id": request.user.id,

    "file_name": message.attachment_name,

    "file_url": message.attachment.url,

    "file_type": message.attachment_type,

    "file_size": message.attachment_size,

    "caption": message.content,
}
    )

    # Update home for both users
    async_to_sync(
        channel_layer.group_send
    )(
        f"user_{request.user.id}",
        {
            "type": "update_home"
        }
    )

    async_to_sync(
        channel_layer.group_send
    )(
        f"user_{other_user.id}",
        {
            "type": "update_home"
        }
    )

    return JsonResponse(
    {
        "success": True,

        "message_id": message.id,

        "sender": request.user.username,

        "sender_id": request.user.id,

        "file_name": message.attachment_name,

        "caption": message.content,

        "file_url": message.attachment.url,

        "file_type": message.attachment_type,

        "file_size": message.attachment_size
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
@csrf_exempt
@require_POST
def ai_assistant(request):

    try:

        # =========================================
        # Read request data
        # =========================================

        data = json.loads(request.body)

        prompt = data.get("prompt", "").strip()


        # =========================================
        # Check empty prompt
        # =========================================

        if not prompt:

            return JsonResponse(
                {
                    "success": False,
                    "error": "Prompt is empty."
                },
                status=400
            )


        # =========================================
        # Ask Ollama / Gemma
        # =========================================

        answer = ask_ai(prompt)


        # =========================================
        # Save AI conversation
        # =========================================

        AIConversation.objects.create(
            user=request.user,
            prompt=prompt,
            response=answer
        )


        # =========================================
        # Return AI response
        # =========================================

        return JsonResponse(
            {
                "success": True,
                "answer": answer
            }
        )


    except Exception as e:

        return JsonResponse(
            {
                "success": False,
                "error": str(e)
            },
            status=500
        )
        
        # ============================================
# AI INSIGHTS FOR NORMAL CHAT CONVERSATIONS
# ============================================

@login_required
@require_POST
def chat_ai_insights(request, user_id):

    try:

        # =========================================
        # 1. Get the other user
        # =========================================

        other_user = get_object_or_404(
            User,
            id=user_id
        )

        # Prevent analyzing a conversation with yourself
        if other_user == request.user:

            return JsonResponse(
                {
                    "success": False,
                    "error": "You cannot analyze a chat with yourself."
                },
                status=400
            )


        # =========================================
        # 2. Read requested AI action
        # =========================================

        data = json.loads(request.body)

        action = data.get("action", "").strip()


        # =========================================
        # 3. Validate requested action
        # =========================================

        allowed_actions = {

            "summary",
            "decisions",
            "tasks",
            "questions",
            "replies"

        }

        if action not in allowed_actions:

            return JsonResponse(
                {
                    "success": False,
                    "error": "Invalid AI action."
                },
                status=400
            )


        # =========================================
        # 4. Retrieve messages between both users
        # =========================================

        messages = Message.objects.filter(

            Q(
                sender=request.user,
                receiver=other_user,
                deleted_for_sender=False
            )

            |

            Q(
                sender=other_user,
                receiver=request.user,
                deleted_for_receiver=False
            )

        ).exclude(

            is_unsent=True

        ).order_by(

            "timestamp"

        )


        # =========================================
        # 5. Extract text messages
        # =========================================

        conversation_messages = []

        for message in messages:

            # Ignore empty messages
            if not message.content.strip():

                continue

            # Determine message sender
            sender_name = message.sender.username

            conversation_messages.append(
                f"{sender_name}: {message.content}"
            )


        # =========================================
        # 6. Check whether conversation exists
        # =========================================

        if not conversation_messages:

            return JsonResponse(
                {
                    "success": False,
                    "error": "There are no text messages to analyze."
                },
                status=400
            )


        # =========================================
        # 7. Limit conversation size
        # =========================================

        # Analyze the latest 100 text messages
        conversation_messages = conversation_messages[-100:]


        conversation_text = "\n".join(
            conversation_messages
        )


        # =========================================
        # 8. Prepare AI instructions
        # =========================================

        instructions = {

            "summary": """

Analyze the conversation and provide:

1. Conversation Overview
2. Key Discussion Points
3. Important Decisions
4. Pending Tasks
5. Unresolved Issues

Keep the summary clear, structured and concise.

""",

            "decisions": """

Analyze the conversation.

Extract only decisions that the participants explicitly
made or clearly agreed upon.

For each decision, explain it briefly.

Do not invent decisions.

If no decisions were made, say so.

""",

            "tasks": """

Analyze the conversation.

Extract actionable tasks.

For each task, provide:

1. Task description
2. Responsible person, if identifiable
3. Deadline, if mentioned

Do not invent deadlines or task assignments.

If no tasks were identified, say so.

""",

            "questions": """

Analyze the conversation.

Identify questions or important issues that remain
unanswered or unresolved.

Explain briefly why each issue may need attention.

Do not invent unanswered questions.

""",

            "replies": """

Analyze the conversation and suggest three possible
replies that the current user could send to the other
participant.

The replies should:

1. Be relevant to the conversation.
2. Sound natural.
3. Have different tones or approaches.
4. Avoid inventing facts.

Clearly separate the three suggested replies.

"""

        }


        # =========================================
        # 9. Construct AI prompt
        # =========================================

        prompt = f"""

You are an intelligent conversation analysis assistant.

You are analyzing a private conversation between two people.

The person requesting the analysis is:

{request.user.username}

The other participant is:

{other_user.username}


IMPORTANT RULES:

- Use only information contained in the conversation.
- Do not invent facts.
- Do not assume information that is not stated.
- Respect the context of the conversation.
- Use clear and readable formatting.


TASK:

{instructions[action]}


CONVERSATION:

{conversation_text}


Provide your analysis now.

"""


        # =========================================
        # 10. Send prompt to Ollama
        # =========================================

        answer = ask_ai(prompt)


        # =========================================
        # 11. Return AI result
        # =========================================

        return JsonResponse(
            {
                "success": True,
                "action": action,
                "answer": answer
            }
        )


    # =============================================
    # 12. Handle errors
    # =============================================

    except json.JSONDecodeError:

        return JsonResponse(
            {
                "success": False,
                "error": "Invalid JSON request."
            },
            status=400
        )


    except Exception as e:

        print("CHAT AI INSIGHTS ERROR:", str(e))

        return JsonResponse(
            {
                "success": False,
                "error": "An error occurred while analyzing the conversation."
            },
            status=500
        )