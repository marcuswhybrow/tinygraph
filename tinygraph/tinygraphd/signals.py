import django.dispatch

poll_start = django.dispatch.Signal()
poll_stop = django.dispatch.Signal()

pre_poll = django.dispatch.Signal(providing_args=['device'])
post_poll = django.dispatch.Signal(providing_args=['device'])

poll_error = django.dispatch.Signal(providing_args=['device', 'message'])

value_change = django.dispatch.Signal(providing_args=['data_instance'])