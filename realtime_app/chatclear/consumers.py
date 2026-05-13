

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        self.other_user_id = self.scope["url_route"]["kwargs"]["user_id"]

        ids = sorted([int(self.user.id), int(self.other_user_id)])
        self.room_group_name = f"chat_{ids[0]}_{ids[1]}"

        # Chat room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Personal room (for home refresh)
        await self.channel_layer.group_add(
            f"user_{self.user.id}",
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        await self.channel_layer.group_discard(
            f"user_{self.user.id}",
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        # =========================
        # CALL REQUEST
        # =========================
        if data.get("type") == "call_request":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "signal_message",
                    "data": {
                        **data,
                        "sender": self.user.username
                    }
                }
            )
            return

        # =========================
        # WEBRTC SIGNALS
        # =========================
        if data.get("type") in ["offer",
            "answer",
            "candidate",
            "call_ended",
            "call_accepted"]:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "signal_message",
                    "data": {
                **data,
                "sender": self.user.username
            }
                }
            )
            return

        # =========================
        # CHAT MESSAGE
        # =========================
        message = data.get("message")

        if not message:
            return

        saved_message = await self.save_message(message)

        # Send message to chat room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": self.user.username,
                "message_id": saved_message.id,
            }
        )

        # Update home for both users
        await self.channel_layer.group_send(
            f"user_{self.user.id}",
            {
                "type": "update_home"
            }
        )

        await self.channel_layer.group_send(
            f"user_{self.other_user_id}",
            {
                "type": "update_home"
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "message_id": event["message_id"],
        }))

    async def signal_message(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    async def update_home(self, event):
        await self.send(text_data=json.dumps({
            "update_home": True
        }))

    @database_sync_to_async
    def save_message(self, message):
        other_user = User.objects.get(id=self.other_user_id)

        saved_message = Message.objects.create(
            sender=self.user,
            receiver=other_user,
            content=message
        )

        return saved_message