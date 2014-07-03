import datetime
import json
import logging

import backoff
import pytz
import requests


log = logging.getLogger(__name__)


class DataSet(object):

    """Client for writing to a Performance Platform data-set"""

    def __init__(self, url, token=None, dry_run=False):
        self.url = url
        self.token = token
        self.dry_run = dry_run

    @staticmethod
    def from_config(config):
        return DataSet(
            config['url'],
            config['token'],
            config['dry_run']
        )

    @staticmethod
    def from_name(api_url, name, dry_run=False):
        """
            doesn't require a token config param
            as all of our data is currently public
        """
        return DataSet(
            '/'.join([api_url, name]).rstrip('/'),
            dry_run=dry_run
        )

    @staticmethod
    def from_group_and_type(api_url, data_group, data_type, dry_run=False,
                            token=None):
        return DataSet(
            '/'.join([api_url, data_group, data_type]).rstrip('/'),
            token,
            dry_run=dry_run,
        )

    def set_token(self, token):
        if token is None:
            raise Exception("You must pass a token to add a token")

        self.token = token
        return self

    def get(self):
        headers = _make_headers()
        if self.dry_run:
            _log_request('GET', self.url, headers)
        else:
            get = requests.get

            response = get(
                url=self.url,
                headers=headers
            )
            try:
                response.raise_for_status()
            except:
                log.error('[PP: {}]\n{}'.format(
                    self.url, response.text))
                raise

            log.debug('[PP] {}'.format(response.text))

    def post(self, records):
        headers = _make_headers(self.token)
        data = _encode_json(records)

        if self.dry_run:
            _log_request('POST', self.url, headers, data)
        else:
            headers, data = _gzip_payload(headers, data)

            post = _exponential_backoff(requests.post)

            response = post(
                url=self.url,
                headers=headers,
                data=data)

            try:
                response.raise_for_status()
            except:
                log.error('[PP: {}]\n{}'.format(
                    self.url, response.text))
                raise

            log.debug('[PP] {}'.format(response.text))

    def empty_data_set(self):
        headers = _make_headers(self.token)
        data = _encode_json([])

        if self.dry_run:
            _log_request('PUT', self.url, headers, data)
        else:
            response = requests.put(
                url=self.url,
                headers=headers,
                data=data)
            try:
                response.raise_for_status()
            except:
                log.error('[PP: {}]\n{}'.format(
                    self.url, response.text))
                raise

            log.debug('[PP] {}'.format(response.text))


class JsonEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            if obj.tzinfo is None:
                obj = obj.replace(tzinfo=pytz.UTC)
            return obj.isoformat()
        return super(JsonEncoder, self).default(obj)


def _log_request(method, url, headers, body):
    log.info('HTTP {} to \'{}\'\nheaders: {}\nbody: {}'.format(
        method, url, headers, body))


def _make_headers(token=False):
    headers = {}
    if token is not False:
        headers['Authorization'] = 'Bearer {}'.format(token)
        headers['Content-type'] = 'application/json'
    else:
        headers['Accept'] = 'application/json, text/javascript'

    return headers


def _encode_json(data):
    return json.dumps(data, cls=JsonEncoder)


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


# A backoff decorator that can be used to wrap requests functions
# The decorator will retry on 502 and 503 responses
_exponential_backoff = backoff.on_predicate(
    backoff.expo,
    lambda response: response.status_code in [502, 503],
    max_tries=5)
