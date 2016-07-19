from django import forms

from extuser.models import ExtUser
from private_message.models import Message


class SendMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('from_user', 'to_user', 'text')
        widgets = {
            'to_user': forms.Select(attrs={'class': 'form-control'}),
            'from_user': forms.HiddenInput(),
            'text': forms.Textarea(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super(SendMessageForm, self).__init__(*args, **kwargs)
        self.fields['to_user'].queryset = ExtUser.objects.filter(is_active=True)
