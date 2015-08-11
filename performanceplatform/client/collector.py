import logging
from performanceplatform.client.base import BaseClient


log = logging.getLogger(__name__)


class CollectorAPI(BaseClient):
    def __init__(self, base_url, token, dry_run=False, request_id_fn=None):
        super(CollectorAPI, self).__init__(
            base_url,
            token,
            dry_run,
            request_id_fn)
        self.should_gzip = False

    def get_collector_type(self, collector_type):
        return self._get('/collector-type/{0}'.format(collector_type))

    def list_collector_types(self):
        return self._get('/collector-type')

    def get_collector(self, collector):
        return self._get('/collector/{0}'.format(collector))

    def list_collectors(self):
        return self._get('/collector')
