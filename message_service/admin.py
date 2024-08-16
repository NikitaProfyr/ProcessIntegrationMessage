from django.contrib import admin
from django.contrib.admin import ModelAdmin

from message_service.models import Mail, Message, ImapServer, FileMessage


class FileMessageInline(admin.StackedInline):
    model = FileMessage
    extra = 1


@admin.register(Mail)
class MailModelAdmin(ModelAdmin):
    model = Mail
    list_display = ["login", "password", "server"]


@admin.register(Message)
class MessageModelAdmin(ModelAdmin):
    model = Message
    list_display = ["title", "date_send", "date_receiving"]
    inlines = [FileMessageInline]


@admin.register(ImapServer)
class ImapServerModelAdmin(ModelAdmin):
    model = ImapServer
