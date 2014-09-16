import requests
import logging
import backoff
import pkg_resources
from functools import wraps

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

    @property
    def base_url(self):
        return self._base_url

    @property
    def token(self):
        return self._token

    @property
    def dry_run(self):
        return self._dry_run

    def _get(self, path):
        return self._request('GET', path)

    def _post(self, path, data):
        return self._request('POST', path, data)

    def _put(self, path, data):
        return self._request('PUT', path, data)

    def get_version(self):
        return pkg_resources.\
            get_distribution('performanceplatform-client').version

    def _request(self, method, path, data=None):
        json = None
        url = self._base_url + path
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Performance Platform Client {}'.format(
                self.get_version()),
            'Request-Id': self._request_id_fn(),
        }

        if self._token is not None:
            headers['Authorization'] = 'Bearer ' + self._token
        if data is not None:
            headers['Content-Type'] = 'application/json'

        if self._dry_run:
            log.info('HTTP {} to "{}"\nheaders: {}'.format(
                method, url, headers))
        else:
            if data is not None:
                headers, data = _gzip_payload(headers, data)
            response = _exponential_backoff(requests.request)(
                method, url, headers=headers, data=data)

            try:
                response.raise_for_status()
            except:
                log.error('[PP-C] {}'.format(response.text))
                raise

            log.debug('[PP-C] {}'.format(response.text))

            json = response.json()

        return json


def return_none_on(status_code):
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except requests.HTTPError as e:
                if e.response.status_code == status_code:
                    return
                else:
                    raise
        return wrapped
    return decorator


def _gzip_payload(headers, data):
    if len(data) > 2048:
        headers['Content-Encoding'] = 'gzip'
        import gzip
        from io import BytesIO
        zipped_data = BytesIO()
        with gzip.GzipFile(filename='', mode='wb', fileobj=zipped_data) as f:
            f.write(data.encode())
        zipped_data.seek(0)

        return headers, zipped_data
    return headers, data


_exponential_backoff = backoff.on_predicate(
    backoff.expo,
    lambda response: response.status_code in [502, 503],
    max_tries=5)
