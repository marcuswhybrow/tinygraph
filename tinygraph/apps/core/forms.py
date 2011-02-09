from django import forms
from core.models import MibUpload



class MibUploadForm(forms.ModelForm):
    class Meta:
        model = MibUpload
        exclude = ('system', 'already_existed')