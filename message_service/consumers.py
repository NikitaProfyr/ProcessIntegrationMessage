import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile

from message_service.mail_service import MailServiceManager, get_all_messages
from message_service.models import Mail, Message, FileMessage
from message_service.serializers import MessageSerializer, MessageFileSerializer


async def message_integration(login, mail_pass, server):
    """
    Интеграция сообщений из почтового сервера и сохранение их в базе данных.

    :param login: Логин для доступа к почтовому серверу.
    :param mail_pass: Пароль для доступа к почтовому серверу.
    :param server: URL почтового сервера.

    Процесс включает следующие шаги:
    1. Получение объекта Mail из базы данных по логину.
    2. Создание и использование менеджера для работы с почтовыми сообщениями.
    3. Установка идентификаторов сообщений для папки "inbox".
    4. Для каждого сообщения:
       - Создание нового объекта Message и сохранение его в базе данных.
       - Создание и сохранение объектов FileMessage для каждого прикрепленного файла.
    """
    mail = await Mail.objects.filter(login=login).afirst()
    async with MailServiceManager(login, mail_pass, server) as mail_manager:
        await mail_manager.set_message_ids("inbox")
        async for msg in mail_manager.get_messages():
            message = Message(
                title=msg.get("title"),
                date_send=msg.get("date_send"),
                date_receiving=msg.get("date_received"),
                text_message=msg.get("content"),
                mail=mail,
            )
            await message.asave()

            message = await Message.objects.filter(pk=message.pk).afirst()

            if message is not None:
                for file in msg["files"]:
                    file_instance = FileMessage(
                        message=message,
                        file=ContentFile(file["payload"], name=file["file_name"]),
                    )
                    await file_instance.asave()


class WSConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.ws_data = None

    async def connect(self):
        await self.accept()
        self.ws_data = {"status": 300, "msg": "", "messages": []}

    async def disconnect(self, close_code):

        await self.close()

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)

        await self.send(text_data=json.dumps(self.ws_data))
        try:
            await message_integration(
                str(data["login"]), str(data["password"]), str(data["server"])
            )
            self.ws_data["status"] = 200
            # self.ws_data.update()
            await self.send(text_data=json.dumps(self.ws_data))

            async for item in get_all_messages():
                files = []
                serializer = MessageSerializer(item)
                response_data = serializer.data
                response_data["files"] = files

                async for file in item.files.all():
                    file_data = MessageFileSerializer(file)
                    files.append(file_data.data)

                self.ws_data["messages"].append(response_data)
                await self.send(text_data=json.dumps(self.ws_data))
        except Exception as err:
            print(err)
            self.ws_data["status"] = 400
            self.ws_data["msg"] = (
                "Проблема при получения данных, проверьте учетные данные"
            )
            await self.send(text_data=json.dumps(self.ws_data))
            await self.close()
