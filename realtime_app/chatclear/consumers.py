


# import json

# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# from django.contrib.auth.models import User

# from .models import Message


# class ChatConsumer(AsyncWebsocketConsumer):

#     # =========================================================
#     # CONNECT
#     # =========================================================

#     async def connect(self):

#         self.user = self.scope["user"]

#         # Reject anonymous users
#         if self.user.is_anonymous:
#             await self.close()
#             return

#         self.other_user_id = (
#             self.scope["url_route"]["kwargs"]["user_id"]
#         )

#         # Create common room name
#         ids = sorted([
#             int(self.user.id),
#             int(self.other_user_id)
#         ])

#         self.room_group_name = (
#             f"chat_{ids[0]}_{ids[1]}"
#         )

#         # =====================================================
#         # CHAT ROOM
#         # =====================================================

#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#         # =====================================================
#         # PERSONAL USER ROOM
#         # Used for home-page updates
#         # =====================================================

#         await self.channel_layer.group_add(
#             f"user_{self.user.id}",
#             self.channel_name
#         )

#         await self.accept()


#     # =========================================================
#     # DISCONNECT
#     # =========================================================

#     async def disconnect(self, close_code):

#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#         await self.channel_layer.group_discard(
#             f"user_{self.user.id}",
#             self.channel_name
#         )


#     # =========================================================
#     # RECEIVE MESSAGE FROM BROWSER
#     # =========================================================

#     async def receive(self, text_data):

#         data = json.loads(text_data)

#         # =====================================================
#         # CALL REQUEST
#         # =====================================================

#         if data.get("type") == "call_request":

#             await self.channel_layer.group_send(
#                 self.room_group_name,
#         {
#             "type": "signal_message",
#             "data": {
#                 **data,
#                 "sender": self.user.username,
#                 "sender_id": self.user.id
#             }
#         }
#             )

#             return


#         # =====================================================
#         # WEBRTC SIGNALS
#         # =====================================================

#         if data.get("type") in [
#              "offer",
#          "answer",
#            "candidate",
#         "call_ended",
#          "call_accepted",
#         "call_rejected"
#         ]:

#             await self.channel_layer.group_send(
#                 self.room_group_name,
#         {
#             "type": "signal_message",
#             "data": {
#                 **data,
#                 "sender": self.user.username,
#                 "sender_id": self.user.id
#             }
#         }
#             )

#             return


#         # =====================================================
#         # NORMAL CHAT MESSAGE
#         # =====================================================

#         if data.get("type") == "chat_message":

#             message = data.get(
#                 "message",
#                 ""
#             ).strip()

#             # Empty message
#             if not message:
#                 return

#             # Save message
#             saved_message = await self.save_message(
#                 message
#             )

#             # =================================================
#             # SEND TO BOTH USERS
#             # =================================================

#             await self.channel_layer.group_send(
#                 self.room_group_name,
#     {
#         "type": "chat_message",
#         "message": message,
#         "sender": self.user.username,
#         "sender_id": self.user.id,
#         "message_id": saved_message.id,
#     }
#             )

#             # =================================================
#             # UPDATE HOME PAGE
#             # =================================================

#             await self.channel_layer.group_send(
#                 f"user_{self.user.id}",
#                 {
#                     "type": "update_home"
#                 }
#             )

#             await self.channel_layer.group_send(
#                 f"user_{self.other_user_id}",
#                 {
#                     "type": "update_home"
#                 }
#             )

#             return


#         # =====================================================
#         # UNKNOWN MESSAGE TYPE
#         # =====================================================

#         print(
#             "Unknown WebSocket message:",
#             data
#         )


#     # =========================================================
#     # CHAT MESSAGE EVENT
#     # This is called by group_send()
#     # =========================================================

#     async def chat_message(self, event):

#          await self.send(
#         text_data=json.dumps({
#             "type": "chat_message",
#             "message": event["message"],
#             "sender": event["sender"],
#             "sender_id": event["sender_id"],
#             "message_id": event["message_id"],
#         })
#         )


#     # =========================================================
#     # FILE MESSAGE EVENT
#     # =========================================================

#     async def file_message(self, event):
#        await self.send(
#         text_data=json.dumps({
#             "type": "file_message",
#             "message_id": event["message_id"],
#             "sender": event["sender"],
#             "sender_id": event["sender_id"],
#             "file_name": event["file_name"],
#             "file_url": event["file_url"],
#             "file_type": event["file_type"],
#             "file_size": event["file_size"],
#             "caption": event.get(
#                 "caption",
#                 ""
#             ),
#         })
#     )


#     # =========================================================
#     # WEBRTC SIGNAL EVENT
#     # =========================================================

#     async def signal_message(self, event):

#         await self.send(
#             text_data=json.dumps(
#                 event["data"]
#             )
#         )


#     # =========================================================
#     # HOME PAGE UPDATE
#     # =========================================================

#     async def update_home(self, event):

#         await self.send(
#             text_data=json.dumps({

#                 "update_home": True

#             })
#         )


#     # =========================================================
#     # SAVE TEXT MESSAGE
#     # =========================================================

#     @database_sync_to_async
#     def save_message(self, message):

#         other_user = User.objects.get(
#             id=self.other_user_id
#         )

#         saved_message = Message.objects.create(

#             sender=self.user,

#             receiver=other_user,

#             content=message

#         )

#         return saved_message


import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from django.contrib.auth.models import User

from .models import Message


class ChatConsumer(AsyncWebsocketConsumer):

    # =========================================================
    # CONNECT
    # =========================================================

    async def connect(self):

        self.user = self.scope["user"]

        # Reject anonymous users
        if self.user.is_anonymous:
            await self.close()
            return

        self.other_user_id = (
            self.scope["url_route"]["kwargs"]["user_id"]
        )

        # Create common room name
        ids = sorted([
            int(self.user.id),
            int(self.other_user_id)
        ])

        self.room_group_name = (
            f"chat_{ids[0]}_{ids[1]}"
        )

        # =====================================================
        # CHAT ROOM
        # =====================================================

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # =====================================================
        # PERSONAL USER ROOM
        # Used for home-page updates
        # =====================================================

        await self.channel_layer.group_add(
            f"user_{self.user.id}",
            self.channel_name
        )

        await self.accept()

        print(
            f"WebSocket connected: "
            f"{self.user.username} -> "
            f"{self.other_user_id}"
        )

    # =========================================================
    # DISCONNECT
    # =========================================================

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        await self.channel_layer.group_discard(
            f"user_{self.user.id}",
            self.channel_name
        )

        print(
            f"WebSocket disconnected: "
            f"{self.user.username}"
        )

    # =========================================================
    # RECEIVE MESSAGE FROM BROWSER
    # =========================================================

    async def receive(self, text_data):

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            print("Invalid WebSocket JSON:", text_data)
            return

        print(
            "WebSocket received:",
            data
        )

        # =====================================================
        # CALL REQUEST
        # =====================================================

        if data.get("type") == "call_request":

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "signal_message",

                    "data": {
                        **data,

                        "sender":
                            self.user.username,

                        "sender_id":
                            self.user.id
                    }
                }
            )

            return

        # =====================================================
        # WEBRTC SIGNALS
        # =====================================================

        if data.get("type") in [
            "offer",
            "answer",
            "candidate",
            "call_ended",
            "call_accepted",
            "call_rejected"
        ]:

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "signal_message",

                    "data": {
                        **data,

                        "sender":
                            self.user.username,

                        "sender_id":
                            self.user.id
                    }
                }
            )

            return

        # =====================================================
        # NORMAL CHAT MESSAGE
        # =====================================================

        if data.get("type") == "chat_message":

            message = data.get(
                "message",
                ""
            ).strip()

            # Ignore empty messages
            if not message:
                return

            # Save message in database
            saved_message = await self.save_message(
                message
            )

            # =================================================
            # SEND MESSAGE TO BOTH USERS
            # =================================================

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",

                    "message":
                        message,

                    "sender":
                        self.user.username,

                    "sender_id":
                        self.user.id,

                    "message_id":
                        saved_message.id
                }
            )

            # =================================================
            # UPDATE HOME PAGE FOR BOTH USERS
            # =================================================

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

            return

        # =====================================================
        # UNKNOWN MESSAGE TYPE
        # =====================================================

        print(
            "Unknown WebSocket message:",
            data
        )

    # =========================================================
    # CHAT MESSAGE EVENT
    # =========================================================

    async def chat_message(self, event):

        await self.send(
            text_data=json.dumps(
                {
                    "type":
                        "chat_message",

                    "message":
                        event["message"],

                    "sender":
                        event["sender"],

                    "sender_id":
                        event["sender_id"],

                    "message_id":
                        event["message_id"]
                }
            )
        )

    # =========================================================
    # FILE MESSAGE EVENT
    # =========================================================

    async def file_message(self, event):

        await self.send(
            text_data=json.dumps(
                {
                    "type":
                        "file_message",

                    "message_id":
                        event["message_id"],

                    "sender":
                        event["sender"],

                    "sender_id":
                        event["sender_id"],

                    "file_name":
                        event["file_name"],

                    "file_url":
                        event["file_url"],

                    "file_type":
                        event["file_type"],

                    "file_size":
                        event["file_size"],

                    "caption":
                        event.get(
                            "caption",
                            ""
                        )
                }
            )
        )

    # =========================================================
    # WEBRTC SIGNAL EVENT
    # =========================================================

    async def signal_message(self, event):

        await self.send(
            text_data=json.dumps(
                event["data"]
            )
        )

    # =========================================================
    # HOME PAGE UPDATE
    # =========================================================

    async def update_home(self, event):

        await self.send(
            text_data=json.dumps(
                {
                    "type":
                        "update_home"
                }
            )
        )

    # =========================================================
    # SAVE TEXT MESSAGE
    # =========================================================

    @database_sync_to_async
    def save_message(self, message):

        other_user = User.objects.get(
            id=self.other_user_id
        )

        saved_message = Message.objects.create(
            sender=self.user,
            receiver=other_user,
            content=message
        )

        return saved_message