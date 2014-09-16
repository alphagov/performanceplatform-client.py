import mock
from nose.tools import eq_
from requests import Response
from hamcrest import has_entries, match_equality

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
    def test_get_data_set_should_still_return_None(self, mock_request):
        response = Response()
        response.status_code = 404
        mock_request.return_value = response
        mock_request.__name__ = 'get'

        api = AdminAPI('http://admin.api', 'token')
        data_set = api.get_data_set('foo', 'bar')

        eq_(data_set, None)
