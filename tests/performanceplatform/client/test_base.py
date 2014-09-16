import mock
from requests import Response
from nose.tools import eq_
from hamcrest import has_entries, match_equality, starts_with

from performanceplatform.client.base import BaseClient


def make_response(status_code=200, content=''):
    resp = Response()
    resp.status_code = status_code
    resp._content = content

    return resp


class TestBaseClient(object):
    @mock.patch('requests.request')
    def test_request_has_correct_headers(self, mock_request):
        mock_request.__name__ = 'request'

        client = BaseClient('http://admin.api', 'token')
        client._get('/foo')

        mock_request.assert_called_with(
            'GET',
            'http://admin.api/foo',
            headers = match_equality(has_entries({
                'Accept': 'application/json',
                'Authorization': 'Bearer token',
                'User-Agent': starts_with('Performance Platform Client'),
            })),
            data=None,
        )

    @mock.patch('requests.request')
    def test_post_has_content_type_header(self, mock_request):
        mock_request.__name__ = 'request'

        client = BaseClient('http://admin.api', 'token')
        client._post('/foo', 'bar')

        mock_request.assert_called_with(
            'POST',
            'http://admin.api/foo',
            headers = match_equality(has_entries({
                'Accept': 'application/json',
                'Authorization': 'Bearer token',
                'User-Agent': starts_with('Performance Platform Client'),
                'Content-Type': 'application/json',
            })),
            data='bar',
        )

    @mock.patch('time.sleep')
    @mock.patch('requests.request')
    def test_request_backs_off_on_bad_gateway(self, mock_request, mock_sleep):
        good = make_response(content='[]')
        bad = make_response(status_code=502)

        mock_request.side_effect = [bad, bad, good]
        mock_request.__name__ = 'request'

        client = BaseClient('http://admin.api', 'token')
        client._get('/foo')

        eq_(mock_request.call_count, 3)
