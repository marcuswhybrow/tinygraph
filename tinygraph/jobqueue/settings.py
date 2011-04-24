from django.conf import settings

ADDRESS = getattr(settings, 'BEANSTALK_ADDRESS', 'localhost')
PORT = getattr(settings, 'BEANSTALK_PORT', 11300)

JOB_TYPES = getattr(settings, 'JOB_TYPES', (
    'mib_integration',
    'mib_disintegration',
))