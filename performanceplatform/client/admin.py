import logging
import requests
import urllib

import backoff
import pkg_resources

log = logging.getLogger(__name__)

try:
    url_quote = urllib.quote_plus
except AttributeError:
    url_quote = urllib.parse.quote_plus


class AdminAPI(object):

    def __init__(self, url, token, dry_run=False, request_id_fn = None):
        self.url = url
        self.token = token
        self.dry_run = dry_run
        if request_id_fn:
            self.request_id_fn = request_id_fn
        else:
            self.request_id_fn = lambda: "Not-Set"

    def get_data_set(self, data_group, data_type):
        query_result = self._get(
            '/data-sets?data-group={0}&data-type={1}'.format(data_group,
                                                             data_type))

        if query_result is not None:
            query_result = query_result[0] if len(query_result) > 0 else None

        return query_result

    def get_data_set_by_name(self, name):
        return self._get('/data-sets/{0}'.format(name))

    def list_data_sets(self):
        return self._get('/data-sets')

    def get_user(self, email):
        return self._get(
            '/users/{0}'.format(url_quote(email)))

    def get_version(self):
        return pkg_resources.\
            get_distribution('performanceplatform-client').version

    def _get(self, path):
        json = None
        url = '{0}{1}'.format(self.url, path)
        headers = {
            'Authorization': 'Bearer {0}'.format(self.token),
            'Accept': 'application/json',
            'User-Agent': 'Performance Platform Client {}'.format(
                self.get_version()),
            'Request-Id': self.request_id_fn()
        }

        if self.dry_run:
            log.info('HTTP GET to "{0}"\nheaders: {1}'.format(url, headers))
        else:
            response = _exponential_backoff(requests.get)(url, headers=headers)

            if response.status_code != 404:
                try:
                    response.raise_for_status()
                except:
                    log.error('[PP-C] {0}'.format(response.text))
                    raise

                log.debug('[PP-C] {0}'.format(response.text))

                json = response.json()

        return json

_exponential_backoff = backoff.on_predicate(
    backoff.expo,
    lambda response: response.status_code in [502, 503],
    max_tries=5)
