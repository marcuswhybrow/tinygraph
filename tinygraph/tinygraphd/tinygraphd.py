from utils import PollDaemon
from tinygraph.apps.core.models import Rule
from utils import logging

class TinyGraphDaemon(PollDaemon):
    def poll(self):
        # TODO Replace with SNMP polling code
        logging.info('Poll - There are %s rules in the DB' % Rule.objects.count())