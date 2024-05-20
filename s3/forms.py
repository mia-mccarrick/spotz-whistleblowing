from django import forms
from .models import Upload


class UploadForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['priority'].required = True
    class Meta:
        model = Upload
        fields = ['title', 'user_comment', 'file', 'priority']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ['admin_comment']

