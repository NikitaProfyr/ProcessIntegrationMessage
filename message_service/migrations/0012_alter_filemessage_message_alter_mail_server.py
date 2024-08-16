# Generated by Django 4.2 on 2024-08-13 23:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("message_service", "0011_alter_message_unique_together"),
    ]

    operations = [
        migrations.AlterField(
            model_name="filemessage",
            name="message",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="files",
                to="message_service.message",
                verbose_name="Сообщение",
            ),
        ),
        migrations.AlterField(
            model_name="mail",
            name="server",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="message_service.imapserver",
                verbose_name="сервер IMAP",
            ),
        ),
    ]
