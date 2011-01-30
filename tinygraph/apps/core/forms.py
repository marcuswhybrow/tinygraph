from django.forms import Form, ModelForm, ValidationError
from django.db.models import Q
from django.template.defaultfilters import slugify
from core.models import Device, MibUpload

class DeviceForm(ModelForm):
    class Meta:
        model = Device
        exclude = ('data_objects',)
    
    def clean_user_given_name(self):
        user_given_name = self.cleaned_data['user_given_name']
        try:
            Device.objects.get(~Q(pk=self.instance.pk), slug=slugify(str(user_given_name)))
        except Device.DoesNotExist:
            return user_given_name
        else:
            raise ValidationError('This name is too similar to another devices name.')

class MibUploadForm(ModelForm):
    class Meta:
        model = MibUpload
        exclude = ('system',)