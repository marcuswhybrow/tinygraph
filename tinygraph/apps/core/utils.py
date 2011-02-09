from django.conf import settings

import logging

LOG_FILENAME = getattr(settings, 'TINYGRAPH_TINYGRAPH_LOG_FILENAME', '/tmp/tinygraph.log')
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')