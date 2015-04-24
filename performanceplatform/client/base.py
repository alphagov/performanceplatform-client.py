import requests
import json
import datetime
import pytz
import logging
import backoff
import pkg_resources
from functools import wraps
import urllib

log = logging.getLogger(__name__)


class ChunkingError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class BaseClient(object):
    def __init__(self, base_url, token, dry_run=False, request_id_fn=None):
        self.should_gzip = True

        if not isinstance(base_url, basestring):
            raise ValueError("base_url must be a string")

        if not isinstance(token, basestring) and token is not None:
            raise ValueError("token must be a string or None")

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

    def _post(self, path, data, chunk_size=0):
        is_iter = hasattr(data, '__iter__')
        if chunk_size > 0:
            if is_iter:
                chunk = []
                chunk_num = 1
                for datum in data:
                    chunk.append(datum)
                    if len(chunk) == chunk_size:
                        log.info('Sending chunk {}'.format(chunk_num))
                        self._request('POST', path, chunk)
                        chunk = []
                        chunk_num += 1

                if len(chunk) > 0:
                    log.info('Sending chunk {}'.format(chunk_num))
                    self._request('POST', path, chunk)
            else:
                raise ChunkingError('Can only chunk on lists')
        else:
            if is_iter and not isinstance(data, (dict, list)):
                data = list(data)
            return self._request('POST', path, data)

    def _put(self, path, data):
        return self._request('PUT', path, data)

    def get_version(self):
        return pkg_resources.\
            get_distribution('performanceplatform-client').version

    def _request(self, method, path, data=None):
        json = None
        url = self.base_url + path
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Performance Platform Client {}'.format(
                self.get_version()),
            'Request-Id': self._request_id_fn(),
        }

        if self.token is not None:
            headers['Authorization'] = 'Bearer ' + self._token
        if data is not None:
            headers['Content-Type'] = 'application/json'

        if self.dry_run:
            log.info('HTTP {} to "{}"\nheaders: {}'.format(
                method, url, headers))
            log.info(data)
        else:
            if data is not None:
                if not isinstance(data, str):
                    data = _encode_json(data)
                headers, data = _gzip_payload(headers, data, self.should_gzip)
            response = _exponential_backoff(requests.request)(
                method, url, headers=headers, data=data)

            try:
                response.raise_for_status()
            except:
                log.error('[PP-C] {}'.format(response.text))
                raise

            if response.status_code != 204:
                json = response.json()

        return json

    def _to_query_string(self, query_parameters):
        query_tuples = []
        for k, v in query_parameters.iteritems():
            if isinstance(v, list):
                for sv in v:
                    query_tuples.append((k, sv))
            else:
                query_tuples.append((k, v))

        if len(query_tuples) > 0:
            query_string = '?' + urllib.urlencode(query_tuples)
        else:
            query_string = ''

        return query_string


def return_none_on(status_code):
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except requests.HTTPError as e:
                if e.response.status_code == status_code:
                    return None
                else:
                    raise
        return wrapped
    return decorator


def _gzip_payload(headers, data, should_gzip):
    if len(data) > 2048 and should_gzip:
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
    lambda response: response.status_code in [500, 502, 503],
    max_tries=5)


class JsonEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            if obj.tzinfo is None:
                obj = obj.replace(tzinfo=pytz.UTC)
            return obj.isoformat()
        return super(JsonEncoder, self).default(obj)


def _encode_json(data):
    return json.dumps(data, cls=JsonEncoder)
