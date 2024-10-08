# Generated by Django 4.2 on 2024-08-11 13:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("message_service", "0006_rename_sever_mail_server"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="imapserver",
            options={
                "verbose_name": "IMAP Сервер",
                "verbose_name_plural": "IMAP Сервера",
            },
        ),
        migrations.AddField(
            model_name="message",
            name="id_message",
            field=models.CharField(
                default=123, unique=True, verbose_name="Идентификатор сообщения"
            ),
            preserve_default=False,
        ),
    ]
