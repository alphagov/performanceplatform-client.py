import mock
from requests import Response
from nose.tools import eq_, assert_raises
from hamcrest import (
    has_entries, match_equality, starts_with,
    assert_that, calling, raises, is_not
)

from performanceplatform.client.base import BaseClient, ChunkingError


def make_response(status_code=200, content=''):
    resp = Response()
    resp.status_code = status_code
    resp._content = content

    return resp


class TestBaseClient(object):
    def test_url_must_be_a_string(self):
        for base_url in [None, 123]:
            assert_raises(ValueError, BaseClient, base_url, '')
        BaseClient('', '')

    def test_token_must_be_none_or_string(self):
        assert_raises(ValueError, BaseClient, '', 123)
        BaseClient('', None)
        BaseClient('', '')

    @mock.patch('requests.request')
    def test_request_has_correct_headers(self, mock_request):
        mock_request.__name__ = 'request'

        client = BaseClient('http://admin.api', 'token')
        client._get('/foo')

        mock_request.assert_called_with(
            'GET',
            'http://admin.api/foo',
            headers=match_equality(has_entries({
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

    @mock.patch('requests.request')
    def test_post_can_be_chunked(self, mock_request):
        mock_request.__name__ = 'request'

        client = BaseClient('http://admin.api', 'token')
        client._post('/foo', [1, 2, 3], chunk_size=2)

        eq_(mock_request.call_count, 2)
        mock_request.assert_has_call(
            mock.call(mock.ANY, mock.ANY, headers=mock.ANY, data='[1,2]'),
            mock.call(mock.ANY, mock.ANY, headers=mock.ANY, data='[3]'))

    @mock.patch('requests.request')
    def test_post_not_chunked_by_default(self, mock_request):
        mock_request.__name__ = 'request'

        client = BaseClient('http://admin.api', 'token')
        client._post('/foo', [1, 2, 3])

        eq_(mock_request.call_count, 1)
        mock_request.assert_any_call(
            mock.ANY, mock.ANY, headers=mock.ANY, data='[1, 2, 3]')

    @mock.patch('requests.request')
    def test_only_iterables_can_be_chunked(self, mock_request):
        mock_request.__name__ = 'request'

        client = BaseClient('http://admin.api', 'token')

        assert_that(
            calling(client._post).with_args('/foo', 'bar', chunk_size=1),
            raises(ChunkingError))
        assert_that(
            calling(client._post).with_args('/foo', 1, chunk_size=1),
            raises(ChunkingError))
        assert_that(
            calling(client._post).with_args(
                '/foo', ('b', 'a', 'r'), chunk_size=1),
            is_not(raises(ChunkingError)))
        assert_that(
            calling(client._post).with_args(
                '/foo', ['b', 'a', 'r'], chunk_size=1),
            is_not(raises(ChunkingError)))

    @mock.patch('requests.request')
    def test_iterators_are_evaluated_into_lists_when_not_chunked(
            self, mock_request):
        mock_request.__name__ = 'request'

        client = BaseClient('http://admin.api', 'token')

        assert_that(
            calling(client._post).with_args(
                '/foo',
                iter(['b', 'a', 'r']),
                chunk_size=0),
            is_not(raises(TypeError)))

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

    @mock.patch('requests.request')
    def test_large_payloads_are_compressed(self, mock_request):
        mock_request.__name__ = 'request'

        client = BaseClient('', 'token')
        client._post('', 'x' * 3000)

        mock_request.assert_called_with(
            mock.ANY,
            mock.ANY,
            headers=match_equality(has_entries({
                'Content-Encoding': 'gzip'
            })),
            data=mock.ANY
        )

        gzipped_bytes = mock_request.call_args[1]['data'].getvalue()

        eq_(38, len(gzipped_bytes))

        # Does it look like a gzipped stream of bytes?
        # http://tools.ietf.org/html/rfc1952#page-5
        eq_(b'\x1f'[0], gzipped_bytes[0])
        eq_(b'\x8b'[0], gzipped_bytes[1])
        eq_(b'\x08'[0], gzipped_bytes[2])
