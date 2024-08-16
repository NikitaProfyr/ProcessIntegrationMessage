import aioimaplib

import email
from email import policy

from typing import AsyncIterator, Dict, List

from message_service.models import Message
from message_service.utils import format_message


async def get_all_messages():
    async for message in Message.objects.all().aiterator():
        yield message


class MailServiceManager:
    """
    Класс для управления почтовыми операциями через IMAP.

    Этот класс позволяет подключаться к IMAP-серверу, аутентифицироваться,
    получать идентификаторы сообщений и извлекать содержимое сообщений.

    Attributes:
        login (str): Логин для аутентификации на сервере.
        password (str): Пароль для аутентификации на сервере.
        server (str): Адрес IMAP-сервера.
        message_ids (List[str]): Список идентификаторов сообщений, полученных из почтового ящика.

    Methods:
        set_message_ids: Получает идентификаторы всех сообщений в указанном почтовом ящике.
        get_messages: Извлекает сообщения по идентификаторам и возвращает их содержимое.
    """

    def __init__(self, login: str, password: str, server: str):
        """
        Инициализирует экземпляр `MailServiceManager`.

        Args:
            login (str): Логин для аутентификации на сервере.
            password (str): Пароль для аутентификации на сервере.
            server (str): Адрес IMAP-сервера.
        """
        self.login = login
        self.password = password
        self.server = server
        self.message_ids = []
        self.mail = None

    async def connection(self):
        try:
            self.mail = aioimaplib.IMAP4_SSL(self.server)
            await self.mail.wait_hello_from_server()
            await self.mail.login(self.login, self.password)
        except Exception as err:
            # Handle other exceptions or re-raise if you want to propagate
            raise err

    async def logout(self):
        await self.mail.logout()

    async def __aenter__(self) -> "MailServiceManager":
        """
        Открывает соединение с сервером и выполняет аутентификацию.

        Returns:
            MailServiceManager: Экземпляр класса `MailServiceManager` для использования внутри
            асинхронного контекста менеджера (`async with`).
        """
        await self.connection()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Закрывает соединение с сервером при выходе из асинхронного контекста менеджера.
        """
        await self.logout()

    async def set_message_ids(self, mail_box: str):
        """
        Устанавливает идентификаторы всех сообщений в указанном почтовом ящике.

        Args:
            mail_box (str): Имя почтового ящика для получения сообщений.

        Returns:
            Dict[str, str]: Результат операции. Если поиск был успешным, `message_ids` будет заполнен
            идентификаторами сообщений. В случае ошибки возвращает сообщение об ошибке.
        """
        await self.mail.select(mail_box)
        status, messages = await self.mail.search("ALL")
        if status != "OK":
            await self.mail.logout()
            return {"msg": "Ошибка поиска сообщений"}

        self.message_ids = messages[0].split()
        self.message_ids = [s.decode("ascii") for s in self.message_ids]

    async def get_messages(self) -> AsyncIterator[str]:
        """
        Извлекает сообщения по идентификаторам и возвращает их содержимое.

        Возвращает:
            AsyncIterator[str]: Асинхронный итератор, который генерирует содержимое сообщений.
        """
        for msg_id in self.message_ids:
            status, msg_data = await self.mail.fetch(msg_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[1], policy=policy.default)
            msg = format_message(msg)
            yield msg
