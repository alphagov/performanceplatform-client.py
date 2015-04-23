import mock
import json
from nose.tools import eq_
from requests import Response
from hamcrest import has_entries, match_equality, is_not

from performanceplatform.client.admin import AdminAPI


class TestAdminAPI(object):

    @mock.patch('requests.request')
    def test_get_user(self, mock_request):
        mock_request.__name__ = 'request'
        api = AdminAPI('http://admin.api', 'token')
        api.get_user('foo@bar.com')

        mock_request.assert_called_with(
            'GET',
            'http://admin.api/users/foo%40bar.com',
            headers=match_equality(has_entries({
                'Accept': 'application/json',
                'Authorization': 'Bearer token'
            })),
            data=None,
        )

    @mock.patch('requests.request')
    def test_create_data_group(self, mock_request):
        mock_request.__name__ = 'request'
        data_group_config = {
            'name': 'carers-allowance'
        }
        base_url = 'get_data_group.com'
        api = AdminAPI(base_url, 'token')
        api.create_data_group(data_group_config)
        mock_request.assert_called_with(
            'POST',
            base_url + '/data-groups',
            headers=match_equality(has_entries({
                'Authorization': 'Bearer token',
                'Content-Type': 'application/json',
                'Request-Id': 'Not-Set'})),
            data=json.dumps(data_group_config)
        )

    @mock.patch('requests.request')
    def test_create_data_set(self, mock_request):
        mock_request.__name__ = 'request'
        data_set_config = {'flibble': 'wibble'}
        base_url = 'base.url.com'
        api = AdminAPI(base_url, 'token')
        api.create_data_set(data_set_config)
        mock_request.assert_called_with(
            'POST',
            base_url + '/data-sets',
            headers=match_equality(has_entries({
                'Authorization': 'Bearer token',
                'Content-Type': 'application/json',
                'Request-Id': 'Not-Set',
            })),
            data=json.dumps(data_set_config))

    @mock.patch('requests.request')
    def test_create_transform(self, mock_request):
        mock_request.__name__ = 'request'
        transform_config = {
            'name': 'carers-allowance'
        }
        base_url = 'example.com'
        api = AdminAPI(base_url, 'token')
        api.create_transform(transform_config)
        mock_request.assert_called_with(
            'POST',
            base_url + '/transform',
            headers=match_equality(has_entries({
                'Authorization': 'Bearer token',
                'Content-Type': 'application/json',
                'Request-Id': 'Not-Set'})),
            data=json.dumps(transform_config)
        )

    @mock.patch('requests.request')
    def test_get_data_set(self, mock_request):
        mock_request.__name__ = 'request'
        api = AdminAPI('http://admin.api', 'token')
        api.get_data_set('group', 'type')

        mock_request.assert_called_with(
            'GET',
            'http://admin.api/data-sets?data-group=group&data-type=type',
            headers=match_equality(has_entries({
                'Accept': 'application/json',
                'Authorization': 'Bearer token'
            })),
            data=None,
        )

    @mock.patch('requests.request')
    def test_get_data_set_by_name(self, mock_request):
        mock_request.__name__ = 'request'
        api = AdminAPI('http://admin.api', None)
        data_set = api.get_data_set_by_name('foo_bar')

        mock_request.assert_called_with(
            'GET',
            'http://admin.api/data-sets/foo_bar',
            headers=match_equality(has_entries({
                'Accept': 'application/json',
            })),
            data=None,
        )

    @mock.patch('requests.request')
    def test_get_data_set_transforms(self, mock_request):
        mock_request.__name__ = 'request'
        api = AdminAPI('http://admin.api', None)
        data_set = api.get_data_set_transforms('foo_bar')

        mock_request.assert_called_with(
            'GET',
            'http://admin.api/data-sets/foo_bar/transform',
            headers=match_equality(has_entries({
                'Accept': 'application/json',
            })),
            data=None,
        )

    @mock.patch('requests.request')
    def test_get_data_set_dashboard(self, mock_request):
        mock_request.__name__ = 'request'
        api = AdminAPI('http://admin.api', None)
        data_set = api.get_data_set_dashboard('foo_bar')

        mock_request.assert_called_with(
            'GET',
            'http://admin.api/data-sets/foo_bar/dashboard',
            headers=match_equality(has_entries({
                'Accept': 'application/json',
            })),
            data=None,
        )

    @mock.patch('requests.request')
    def test_get_transform_types(self, mock_request):
        mock_request.__name__ = 'request'
        api = AdminAPI('http://admin.api', 'token')
        api.get_transform_types()

        mock_request.assert_called_with(
            'GET',
            'http://admin.api/transform-type',
            headers=match_equality(has_entries({
                'Accept': 'application/json',
                'Authorization': 'Bearer token'
            })),
            data=None,
        )

    @mock.patch('requests.request')
    def test_make_sure_returns_response(self, mock_request):
        response = Response()
        response.status_code = 200
        response._content = b'[{"data-type":"type"}]'
        mock_request.return_value = response
        mock_request.__name__ = 'get'

        api = AdminAPI('http://admin.api', 'token')
        data_sets = api.list_data_sets()

        eq_(data_sets[0]['data-type'], 'type')

    @mock.patch('requests.request')
    def test_dry_run(self, mock_request):
        api = AdminAPI('http://admin.api', 'token', dry_run=True)
        api.list_data_sets()

        eq_(mock_request.called, False)

    @mock.patch('requests.request')
    def test_get_data_set_should_only_return_one(self, mock_request):
        response = Response()
        response.status_code = 200
        response._content = b'[{"data-type":"type"}]'
        mock_request.return_value = response
        mock_request.__name__ = 'get'

        api = AdminAPI('http://admin.api', 'token')
        data_set = api.get_data_set('foo', 'type')

        eq_(data_set['data-type'], 'type')

    @mock.patch('requests.request')
    def test_get_data_set_should_return_None_if_no_match(self, mock_request):
        response = Response()
        response.status_code = 200
        response._content = b'[]'
        mock_request.return_value = response
        mock_request.__name__ = 'get'

        api = AdminAPI('http://admin.api', 'token')
        data_set = api.get_data_set('foo', 'type')

        eq_(data_set, None)

    @mock.patch('requests.request')
    def test_get_data_set_should_return_None_on_404(self, mock_request):
        response = Response()
        response.status_code = 404
        mock_request.return_value = response
        mock_request.__name__ = 'get'

        api = AdminAPI('http://admin.api', 'token')
        data_set = api.get_data_set('foo', 'bar')

        eq_(data_set, None)

    @mock.patch('requests.request')
    def test_get_data_set_by_name_should_return_None_on_404(
            self, mock_request):
        response = Response()
        response.status_code = 404
        mock_request.return_value = response
        mock_request.__name__ = 'get'

        api = AdminAPI('http://admin.api', 'token')
        data_set = api.get_data_set_by_name('foo_bar')

        eq_(data_set, None)

    @mock.patch('requests.request')
    def test_get_dashboard(self, mock_request):
        mock_request.__name__ = 'request'
        api = AdminAPI('http://admin.api', 'token')
        api.get_dashboard('uuid')

        mock_request.assert_called_with(
            'GET',
            'http://admin.api/dashboard/uuid',
            headers=match_equality(has_entries({
                'Accept': 'application/json',
                'Authorization': 'Bearer token'
            })),
            data=None,
        )

    @mock.patch('requests.request')
    def test_get_dashboard_by_tx_id(self, mock_request):
        mock_request.__name__ = 'request'
        api = AdminAPI('http://admin.api', 'token')
        api.get_dashboard_by_tx_id('dft-some-service')

        mock_request.assert_called_with(
            'GET',
            'http://admin.api/transactions-explorer-service/dft-some-service/dashboard',
            headers=match_equality(has_entries({
                'Accept': 'application/json',
                'Authorization': 'Bearer token'
            })),
            data=None,
        )

    @mock.patch('requests.request')
    def test_list_organisations(self, mock_request):
        mock_request.__name__ = 'request'
        api = AdminAPI('http://admin.api', 'token')
        api.list_organisations()

        mock_request.assert_called_with(
            'GET',
            'http://admin.api/organisation/node',
            headers=match_equality(has_entries({
                'Accept': 'application/json',
                'Authorization': 'Bearer token'
            })),
            data=None,
        )

    @mock.patch('requests.request')
    def test_list_organisations_with_filter(self, mock_request):
        mock_request.__name__ = 'request'
        api = AdminAPI('http://admin.api', 'token')
        api.list_organisations({'type': ['department', 'agency']})

        mock_request.assert_called_with(
            'GET',
            'http://admin.api/organisation/node?type=department&type=agency',
            headers=match_equality(has_entries({
                'Accept': 'application/json',
                'Authorization': 'Bearer token'
            })),
            data=None,
        )

    @mock.patch('requests.request')
    def test_large_payloads_to_admin_app_are_not_compressed(
            self, mock_request):
        mock_request.__name__ = 'request'

        client = AdminAPI('', 'token')
        client._post('', 'x' * 3000)

        mock_request.assert_called_with(
            mock.ANY,
            mock.ANY,
            headers=match_equality(is_not(has_entries({
                'Content-Encoding': 'gzip'
            }))),
            data=mock.ANY
        )

        unzipped_bytes = mock_request.call_args[1]['data']

        eq_(3000, len(unzipped_bytes))

    @mock.patch('requests.request')
    def test_reauth(
            self, mock_request):
        response = Response()
        response.status_code = 204
        response._content = None
        mock_request.return_value = response
        mock_request.__name__ = 'request'

        client = AdminAPI('http://meta.api.com', 'token')
        client.reauth('foo')

        mock_request.assert_called_with(
            'POST',
            'http://meta.api.com/auth/gds/api/users/foo/reauth',
            headers=match_equality(has_entries({
                'Authorization': 'Bearer token',
            })),
            data=None
        )
