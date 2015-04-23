import logging
import urllib
import json

from .base import BaseClient, return_none_on


log = logging.getLogger(__name__)


try:
    url_quote = urllib.quote_plus
except AttributeError:
    url_quote = urllib.parse.quote_plus


class AdminAPI(BaseClient):

    def __init__(self, base_url, token, dry_run=False, request_id_fn=None):
        super(AdminAPI, self).__init__(
            base_url,
            token,
            dry_run,
            request_id_fn)
        self.should_gzip = False

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

    def get_data_set_transforms(self, name):
        return self._get('/data-sets/{0}/transform'.format(name))

    def get_data_set_dashboard(self, name):
        return self._get('/data-sets/{0}/dashboard'.format(name))

    def list_data_sets(self):
        return self._get('/data-sets')

    @return_none_on(404)
    def get_data_group(self, data_group):
        query_result = self._get(
            '/data-groups?name={0}'.format(data_group))

        if query_result is not None:
            query_result = query_result[0] if len(query_result) > 0 else None

        return query_result

    def get_user(self, email):
        return self._get(
            '/users/{0}'.format(url_quote(email)))

    def get_dashboard(self, dashboard_id):
        return self._get(
            '/dashboard/{0}'.format(dashboard_id))

    def get_dashboard_by_tx_id(self, tx_id):
        return self._get(
            '/transactions-explorer-service/{}/dashboard'.format(tx_id),
        )

    def get_transform_types(self):
        return self._get('/transform-type')

    def create_data_set(self, data):
        return self._post('/data-sets', json.dumps(data))

    def create_data_group(self, data):
        return self._post('/data-groups', json.dumps(data))

    def create_transform(self, data):
        return self._post('/transform', json.dumps(data))

    def create_dashboard(self, data):
        return self._post('/dashboard', json.dumps(data))

    def update_dashboard(self, dashboard_id, data):
        return self._put('/dashboard/{}'.format(dashboard_id),
                         json.dumps(data))

    def list_organisations(self, query=None):
        if query:
            path = self._to_query_string(query)
        else:
            path = ''
        return self._get('/organisation/node{}'.format(
            path))

    def list_modules_on_dashboard(self, dashboard_id):
        return self._get('/dashboard/{}/module'.format(dashboard_id))

    def add_module_to_dashboard(self, dashboard_id, data):
        return self._post('/dashboard/{}/module'.format(dashboard_id),
                          json.dumps(data))

    def list_module_types(self):
        return self._get('/module-type')

    def add_module_type(self, data):
        return self._post('/module-type', json.dumps(data))

    def reauth(self, uid):
        return self._post('/auth/gds/api/users/{}/reauth'.format(uid), None)
