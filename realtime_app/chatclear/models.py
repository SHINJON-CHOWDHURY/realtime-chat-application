from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):

    # ===============================
    # Sender and Receiver
    # ===============================

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_messages"
    )

    # ===============================
    # Message Content
    # ===============================

    # Text message
    # blank=True allows file-only messages
    content = models.TextField(
        blank=True
    )

    # ===============================
    # File Attachment
    # ===============================

    # Stores any type of uploaded file
    attachment = models.FileField(
        upload_to="chat_files/",
        blank=True,
        null=True
    )

    # Original file name
    attachment_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # MIME type, for example:
    # image/jpeg
    # video/mp4
    # application/pdf
    attachment_type = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # File size in bytes
    attachment_size = models.BigIntegerField(
        blank=True,
        null=True
    )

    # ===============================
    # Timestamp
    # ===============================

    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    # ===============================
    # WhatsApp-style Delete Features
    # ===============================

    # Remove only for sender
    deleted_for_sender = models.BooleanField(
        default=False
    )

    # Remove only for receiver
    deleted_for_receiver = models.BooleanField(
        default=False
    )

    # Unsend for both users
    is_unsent = models.BooleanField(
        default=False
    )

    # ===============================
    # String Representation
    # ===============================

    def __str__(self):

        if self.is_unsent:
            return "Message unsent"

        if self.attachment:
            return self.attachment_name or "File attachment"

        return self.content or "Empty message"


class UserProfile(models.Model):

    # ===============================
    # User
    # ===============================

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    # ===============================
    # Profile Picture
    # ===============================

    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True
    )

    # ===============================
    # String Representation
    # ===============================

    def __str__(self):
        return self.user.username