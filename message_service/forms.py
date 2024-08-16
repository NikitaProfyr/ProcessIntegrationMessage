from django.forms import ModelForm

from message_service.models import Mail


class MailForm(ModelForm):
    class Meta:
        model = Mail
        fields = "__all__"
