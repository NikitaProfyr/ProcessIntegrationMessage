# Generated by Django 4.2 on 2024-08-12 13:42

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("message_service", "0010_alter_message_title"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="message",
            unique_together=set(),
        ),
    ]