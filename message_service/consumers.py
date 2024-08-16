import json

from channels.generic.websocket import AsyncWebsocketConsumer

from message_service.mail_service import get_all_messages, message_integration
from message_service.serializers import MessageSerializer, MessageFileSerializer


class WSConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.ws_data = None

    async def connect(self):
        await self.accept()
        self.ws_data = {
            "status": 300,
            "msg": "",
            "message": {},
            "count_messages": 0,
            "load_messages": 0,
        }

    async def disconnect(self, close_code):

        await self.close()

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)

        await self.send(text_data=json.dumps(self.ws_data))
        try:
            count_messages = await message_integration(
                str(data["login"]), str(data["password"]), str(data["server"])
            )
            self.ws_data["status"] = 200
            self.ws_data["count_messages"] = count_messages
            self.ws_data["load_messages"] = count_messages

            await self.send(text_data=json.dumps(self.ws_data))
            async for item in get_all_messages():
                files = []
                serializer = MessageSerializer(item)
                response_data = serializer.data
                response_data["files"] = files

                async for file in item.files.all():
                    file_data = MessageFileSerializer(file)
                    files.append(file_data.data)
                self.ws_data["load_messages"] -= 1
                self.ws_data["message"] = response_data
                await self.send(text_data=json.dumps(self.ws_data))
        except Exception as err:
            print(err)
            self.ws_data["status"] = 400
            self.ws_data["msg"] = (
                "Проблема при получения данных, проверьте учетные данные"
            )
            await self.send(text_data=json.dumps(self.ws_data))
            await self.close()
