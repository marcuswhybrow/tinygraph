import django.dispatch

pre_poll = django.dispatch.Signal(providing_args=['device'])
post_poll = django.dispatch.Signal(providing_args=['device'])

poll_error = django.dispatch.Signal(providing_args=['device', 'message'])

value_change = django.dispatch.Signal(providing_args=['data_instance'])