import requests
import logging
import backoff
import pkg_resources

log = logging.getLogger(__name__)


class BaseClient(object):
    def __init__(self, base_url, token, dry_run=False, request_id_fn=None):
        self._base_url = base_url
        self._token = token
        self._dry_run = dry_run
        if request_id_fn:
            self._request_id_fn = request_id_fn
        else:
            self._request_id_fn = lambda: 'Not-Set'

    def _get(self, path):
        return self._request('GET', path)

    def _post(self, path, data):
        return self._request('POST', path, data)

    def get_version(self):
        return pkg_resources.\
            get_distribution('performanceplatform-client').version

    def _request(self, method, path, data=None):
        url = self._base_url + path
        headers = {
            'Authorization': 'Bearer ' + self._token,
            'Accept': 'application/json',
            'User-Agent': 'Performance Platform Client {}'.format(
                self.get_version()),
            'Request-Id': self._request_id_fn(),
        }
        json = None

        if data is not None:
            headers['Content-Type'] = 'application/json'

        if self._dry_run:
            log.info('HTTP {} to "{}"\nheaders: {}'.format(
                method, url, headers))
        else:
            response = _exponential_backoff(requests.request)(
                method, url, headers=headers, data=data)

            if response.status_code != 404:
                try:
                    response.raise_for_status()
                except:
                    log.error('[PP-C] {}'.format(response.text))
                    raise

                log.debug('[PP-C] {}'.format(response.text))

                json = response.json()

        return json


_exponential_backoff = backoff.on_predicate(
    backoff.expo,
    lambda response: response.status_code in [502, 503],
    max_tries=5)
