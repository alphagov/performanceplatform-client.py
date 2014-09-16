import logging
import urllib

from .base import BaseClient, return_none_on


log = logging.getLogger(__name__)


try:
    url_quote = urllib.quote_plus
except AttributeError:
    url_quote = urllib.parse.quote_plus


class AdminAPI(BaseClient):

    @return_none_on(404)
    def get_data_set(self, data_group, data_type):
        query_result = self._get(
            '/data-sets?data-group={0}&data-type={1}'.format(data_group,
                                                             data_type))

        if query_result is not None:
            query_result = query_result[0] if len(query_result) > 0 else None

        return query_result

    @return_none_on(404)
    def get_data_set_by_name(self, name):
        return self._get('/data-sets/{0}'.format(name))

    def list_data_sets(self):
        return self._get('/data-sets')

    def get_user(self, email):
        return self._get(
            '/users/{0}'.format(url_quote(email)))
