from django.views.generic.simple import direct_to_template
from definitions.models import DataObject
from definitions.models import Package, MibUpload
from definitions.forms import MibUploadForm

def data_object_list(request):
    return direct_to_template(request, 'definitions/data_object_list.html', {
        'root_data_object_list': DataObject.objects.root_only().select_related(),
    })

def mib_upload_list(request):
    if request.method == 'POST':
        form = MibUploadForm(request.POST, request.FILES)
        if form.is_valid():
            mib_upload = form.save()
            return direct_to_template(request, 'definitions/mib_upload_uploaded.html', {
                'mib_upload': mib_upload,
            })
    else:
        form = MibUploadForm()

    return direct_to_template(request, 'definitions/mib_upload_list.html', {
        'mib_uploads': MibUpload.objects.filter(system=False),
        'form': form,
    })

def package_list(request):
    return direct_to_template(request, 'definitions/packages/package_list.html', {
        'custom_packages': Package.objects.filter(editable=True),
        'system_packages': Package.objects.filter(editable=False),
    })

def package_detail(request, package_slug):
    package = get_object_or_404(Package, slug=package_slug)
    return direct_to_template(request, 'definitions/packages/package_detail.html', {
        'package': package,
    })