from django import forms

from extuser.models import ExtUser
from private_message.models import Message, FilesForMessage


class SendNewMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('to_user', 'text')
        widgets = {
            'to_user': forms.Select(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super(SendNewMessageForm, self).__init__(*args, **kwargs)
        self.fields['to_user'].queryset = ExtUser.objects.filter(is_active=True)


class SendMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('to_user', 'text')
        widgets = {
            'to_user': forms.HiddenInput(),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
        }
