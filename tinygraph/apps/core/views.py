from django.views.generic.simple import direct_to_template

        
def index(request):
    # It's simple now but will probably require expantion
    return direct_to_template(request, 'core/index.html', {})