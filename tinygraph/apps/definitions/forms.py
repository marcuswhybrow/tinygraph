from django import forms
from tinygraph.apps.definitions.models import MibUpload, Package

class MibUploadForm(forms.ModelForm):
    class Meta:
        model = MibUpload
        exclude = ('system', 'already_existed')

class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        exclude = ('data_objects', 'editable')