from django.views.generic.simple import direct_to_template
from dashboard.models import Board

def index(request):
    try:
        board = Board.objects.get(pk=1)
    except Board.DoesNotExist:
        board = None
    
    return direct_to_template(request, 'dashboard/index.html', {
        'board': board,
    })