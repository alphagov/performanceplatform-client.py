from __future__ import unicode_literals

import datetime
import json
import logging

import pytz

from performanceplatform.client.base import BaseClient


log = logging.getLogger(__name__)


class DataSet(BaseClient):

    """Client for writing to a Performance Platform data-set"""

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
            token=None,
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

        self._token = token
        return self

    def get(self):
        return self._get('')

    def post(self, records):
        return self._post('', _encode_json(records))

    def empty_data_set(self):
        return self._put('', _encode_json([]))


class JsonEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            if obj.tzinfo is None:
                obj = obj.replace(tzinfo=pytz.UTC)
            return obj.isoformat()
        return super(JsonEncoder, self).default(obj)


def _encode_json(data):
    return json.dumps(data, cls=JsonEncoder)
