from datetime import datetime

import mock
from nose.tools import eq_, assert_raises
from requests import Response, HTTPError

from performanceplatform.client import DataSet


class TestDataSet(object):

    def test_from_target(self):
        data_set = DataSet('foo', 'bar')
        eq_(data_set.url, 'foo')
        eq_(data_set.token, 'bar')
        eq_(data_set.dry_run, False)

    def test_from_config(self):
        data_set = DataSet.from_config({
            'url': 'foo',
            'token': 'bar',
            'dry_run': True,
        })
        eq_(data_set.url, 'foo')
        eq_(data_set.token, 'bar')
        eq_(data_set.dry_run, True)

    @mock.patch('performanceplatform.client.requests')
    def test_empty_data_set(self, mock_requests):
        data_set = DataSet('some-url', 'some-token')
        data_set.empty_data_set()
        mock_requests.put.assert_called_with(
            url='some-url',
            headers={
                'Authorization': 'Bearer some-token',
                'Content-type': 'application/json',
            },
            data='[]')

    @mock.patch('requests.post')
    def test_post_data_to_data_set(self, mock_post):
        mock_post.__name__ = 'post'
        data_set = DataSet('foo', 'bar')

        data_set.post({'key': 'value'})

        mock_post.assert_called_with(
            url='foo',
            headers={
                'Authorization': 'Bearer bar',
                'Content-type': 'application/json'
            },
            data='{"key": "value"}'
        )

    @mock.patch('requests.post')
    def test_post_to_data_set(self, mock_post):
        mock_post.__name__ = 'post'
        data_set = DataSet(None, None)

        data_set.post({'key': datetime(2012, 12, 12)})

        mock_post.assert_called_with(
            url=mock.ANY,
            headers=mock.ANY,
            data='{"key": "2012-12-12T00:00:00+00:00"}'
        )

    @mock.patch('requests.post')
    def test_post_large_data_is_compressed(self, mock_post):
        mock_post.__name__ = 'name'
        data_set = DataSet(None, None)

        big_string = "x" * 3000
        data_set.post({'key': big_string})

        mock_post.assert_called_with(
            url=mock.ANY,
            headers={
                'Content-type': 'application/json',
                'Authorization': 'Bearer None',
                'Content-Encoding': 'gzip',
            },
            data=mock.ANY
        )

        call_args = mock_post.call_args

        gzipped_bytes = call_args[1]["data"].getvalue()

        # large repeated string compresses really well - who knew?
        eq_(52, len(gzipped_bytes))

        # Does it look like a gzipped stream of bytes?
        # http://tools.ietf.org/html/rfc1952#page-5
        eq_(b'\x1f'[0], gzipped_bytes[0])
        eq_(b'\x8b'[0], gzipped_bytes[1])
        eq_(b'\x08'[0], gzipped_bytes[2])

    @mock.patch('requests.post')
    def test_raises_error_on_4XX_or_5XX_responses(self, mock_post):
        mock_post.__name__ = 'post'
        data_set = DataSet(None, None)
        response = Response()
        response.status_code = 418
        mock_post.return_value = response
        assert_raises(HTTPError, data_set.post, {'key': 'foo'})

    @mock.patch('requests.post')
    @mock.patch('performanceplatform.client.log')
    def test_logs_on_dry_run(self, mock_log, mock_post):
        mock_post.__name__ = 'post'

        data_set = DataSet(None, None, dry_run=True)
        data_set.post({'key': datetime(2012, 12, 12)})

        eq_(mock_log.info.call_count, 1)
        eq_(mock_post.call_count, 0)

    @mock.patch('time.sleep')
    @mock.patch('requests.post')
    def test_backs_off_on_bad_gateway(self, mock_post, mock_sleep):
        data_set = DataSet(None, None)

        good = Response()
        good.status_code = 200
        bad = Response()
        bad.status_code = 502

        mock_post.side_effect = [bad, bad, good]
        mock_post.__name__ = 'post'

        # No exception should be raised
        data_set.post([{'key': 'foo'}])

    @mock.patch('time.sleep')
    @mock.patch('requests.post')
    def test_backs_off_on_service_unavailable(self, mock_post, mock_sleep):
        data_set = DataSet(None, None)

        good = Response()
        good.status_code = 200
        bad = Response()
        bad.status_code = 503

        mock_post.side_effect = [bad, bad, good]
        mock_post.__name__ = 'post'

        # No exception should be raised
        data_set.post([{'key': 'foo'}])

    @mock.patch('time.sleep')
    @mock.patch('requests.post')
    def test_does_not_back_off_on_forbidden(self, mock_post, mock_sleep):
        data_set = DataSet(None, None)

        good = Response()
        good.status_code = 200
        bad = Response()
        bad.status_code = 403

        mock_post.side_effect = [bad]
        mock_post.__name__ = 'post'

        assert_raises(HTTPError, data_set.post, [{'key': 'foo'}])

    @mock.patch('time.sleep')
    @mock.patch('performanceplatform.client.requests.post')
    def test_fails_after_5_backoffs(self, mock_post, mock_sleep):
        data_set = DataSet(None, None)

        bad = Response()
        bad.status_code = 502

        mock_post.return_value = bad
        mock_post.__name__ = 'post'

        assert_raises(HTTPError, data_set.post, [{'key': 'foo'}])
        eq_(mock_post.call_count, 5)
