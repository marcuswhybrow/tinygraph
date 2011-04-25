from django.views.generic.simple import direct_to_template

def settings(request):
    return direct_to_template(request, 'core/settings.html', {})