

# from django.db import models
# from django.contrib.auth.models import User


# class Message(models.Model):
#     sender = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name="sent_messages"
#     )
#     receiver = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name="received_messages"
#     )

#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     # ===============================
#     # WhatsApp-style delete features
#     # ===============================

#     # Remove only for sender
#     deleted_for_sender = models.BooleanField(default=False)

#     # Remove only for receiver
#     deleted_for_receiver = models.BooleanField(default=False)

#     # Unsend (delete for both)
#     is_unsent = models.BooleanField(default=False)

#     def __str__(self):
#         return self.content


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
    content = models.TextField()

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
    # Instead of deleting row from DB,
    # we mark message as unsent
    is_unsent = models.BooleanField(
        default=False
    )

    # ===============================
    # String Representation
    # ===============================
    def __str__(self):
        if self.is_unsent:
            return "Message unsent"

        return self.content