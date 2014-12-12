from __future__ import unicode_literals

import logging
import urllib

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
        if not isinstance(token, basestring):
            raise Exception("token must be a string")

        self._token = token

    def get(self, query_parameters={}):
        return self._get(self._to_query_string(query_parameters))

    def post(self, records, chunk_size=0):
        return self._post('', records, chunk_size=chunk_size)

    def empty_data_set(self):
        return self._put('', [])

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
