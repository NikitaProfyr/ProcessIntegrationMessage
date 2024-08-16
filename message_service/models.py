from django.core.exceptions import ValidationError
from django.db import models


def upload_to_file(instance: "FileMessage", filename: str) -> str:
    """ "Функция для загрузки файла"""
    return f"message_{instance.message.pk}/file_{filename}"


class ImapServer(models.Model):
    name = models.CharField(max_length=20, verbose_name="Наименование imap сервера")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "IMAP Сервер"
        verbose_name_plural = "IMAP Сервера"


class Mail(models.Model):
    login = models.EmailField(verbose_name="Электронная почта")
    password = models.CharField(
        max_length=20, verbose_name="Пароль для доступа по протоколу IMAP"
    )
    server = models.ForeignKey(
        ImapServer, on_delete=models.SET_NULL, null=True, verbose_name="сервер IMAP"
    )

    class Meta:
        verbose_name = "Электронная почта"
        verbose_name_plural = "Электронные почты"


class Message(models.Model):
    title = models.TextField(verbose_name="Тема сообщения")
    date_send = models.DateTimeField(verbose_name="Дата отправки")
    date_receiving = models.DateTimeField(verbose_name="Дата получения")
    text_message = models.TextField(verbose_name="текст сообщения")
    mail = models.ForeignKey(Mail, on_delete=models.CASCADE, verbose_name="Эл.почта")

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def save(self, *args, **kwargs):
        try:
            # Проверка уникальности записи
            if self.pk is None:
                if Message.objects.filter(
                    title=self.title,
                    date_send=self.date_send,
                    date_receiving=self.date_receiving,
                    text_message=self.text_message,
                    mail=self.mail,
                ).exists():
                    raise ValidationError("Запись с такими данными уже существует.")
            super().save(*args, **kwargs)
        except ValidationError as error:
            print(error.message)


class FileMessage(models.Model):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="files",
        verbose_name="Сообщение",
    )
    file = models.FileField(upload_to=upload_to_file, unique=True, verbose_name="Файл")

    class Meta:
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"
