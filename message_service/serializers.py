from rest_framework import serializers

from message_service.models import Message, FileMessage


class MessageFileSerializer(serializers.ModelSerializer):
    src = serializers.SerializerMethodField()

    class Meta:
        model = FileMessage
        fields = ["src"]

    def get_src(self, obj):
        return obj.file.url


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["title", "date_send", "date_receiving", "text_message"]
