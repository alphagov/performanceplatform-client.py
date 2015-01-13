from datetime import datetime

import mock
import multiprocessing  # quieten the test worker
from nose.tools import eq_, assert_raises
from nose import SkipTest
from requests import Response, HTTPError
from hamcrest import has_entries, match_equality

from performanceplatform.client.data_set import DataSet


class TestDataSet(object):

    def test_from_target(self):
        data_set = DataSet('foo', 'bar')
        eq_(data_set.base_url, 'foo')
        eq_(data_set.token, 'bar')
        eq_(data_set.dry_run, False)

    def test_from_config(self):
        data_set = DataSet.from_config({
            'url': 'foo',
            'token': 'bar',
            'dry_run': True,
        })
        eq_(data_set.base_url, 'foo')
        eq_(data_set.token, 'bar')
        eq_(data_set.dry_run, True)

    def test_from_name(self):
        data_set = DataSet.from_name(
            'foo',
            'woof'
        )
        eq_(data_set.base_url, 'foo/woof')
        eq_(data_set.dry_run, False)

    def test_from_name_with_dry_run(self):
        data_set = DataSet.from_name(
            'foo',
            'woof',
            True
        )
        eq_(data_set.base_url, 'foo/woof')
        eq_(data_set.dry_run, True)

    def test_set_token(self):
        data_set = DataSet.from_name(
            'foo',
            'woof',
            True
        )

        eq_(data_set.token, None)

        data_set.set_token("hotflops69")

        eq_(data_set.token, "hotflops69")

    def test_from_group_and_type(self):
        data_set = DataSet.from_group_and_type(
            'base.url.com',
            'dogs',
            'hair-length'
        )
        eq_(data_set.base_url, 'base.url.com/dogs/hair-length')
        eq_(data_set.dry_run, False)

    def test_from_group_and_type_with_dry_run(self):
        data_set = DataSet.from_group_and_type(
            'base.url.com',
            'dogs',
            'hair-length',
            True,
        )
        eq_(data_set.base_url, 'base.url.com/dogs/hair-length')
        eq_(data_set.dry_run, True)

    @mock.patch('requests.request')
    def test_empty_data_set(self, mock_request):
        mock_request.__name__ = 'request'
        data_set = DataSet('some-url', 'some-token')
        data_set.empty_data_set()
        mock_request.assert_called_with(
            'PUT',
            'some-url',
            headers=mock.ANY,
            data='[]')

    @mock.patch('requests.request')
    def test_post_data_to_data_set(self, mock_request):
        mock_request.__name__ = 'request'
        data_set = DataSet('foo', 'bar')

        data_set.post({'key': 'value'})

        mock_request.assert_called_with(
            'POST',
            'foo',
            headers=mock.ANY,
            data='{"key": "value"}'
        )

    @mock.patch('requests.request')
    def test_post_to_data_set(self, mock_request):
        mock_request.__name__ = 'request'
        data_set = DataSet('', None)

        data_set.post({'key': datetime(2012, 12, 12)})

        mock_request.assert_called_with(
            'POST',
            mock.ANY,
            headers=mock.ANY,
            data='{"key": "2012-12-12T00:00:00+00:00"}'
        )

    @mock.patch('requests.request')
    def test_get_data_set_by_name(self, mock_request):
        mock_request.__name__ = 'request'
        data_set = DataSet.from_name(
            'http://dropthebase.com',
            'my-buff-data-set'
        )

        data_set.get()

        mock_request.assert_called_with(
            'GET',
            'http://dropthebase.com/my-buff-data-set',
            headers=match_equality(has_entries({
                'Accept': 'application/json',
            })),
            data=mock.ANY
        )

    @mock.patch('requests.request')
    def test_get_data_set_by_group_and_type(self, mock_request):
        mock_request.__name__ = 'request'
        data_set = DataSet.from_group_and_type(
            # bit of a gotcha in the /data here
            'http://dropthebase.com/data',
            'famous-knights',
            'dragons-killed'
        )

        data_set.get()

        mock_request.assert_called_with(
            'GET',
            'http://dropthebase.com/data/famous-knights/dragons-killed',
            headers=mock.ANY,
            data=mock.ANY,
        )

    @mock.patch('requests.request')
    def test_get_data_set_by_group_and_type_with_bearer_token(
            self, mock_request):
        mock_request.__name__ = 'request'
        data_set = DataSet.from_group_and_type(
            # bit of a gotcha in the /data here
            'http://dropthebase.com/data',
            'famous-knights',
            'dragons-killed',
            token='token',
        )

        data_set.get()

        mock_request.assert_called_with(
            'GET',
            'http://dropthebase.com/data/famous-knights/dragons-killed',
            headers=mock.ANY,
            data=mock.ANY,
        )

    @mock.patch('requests.request')
    def test_post_to_data_set_by_group_and_type(self, mock_request):
        mock_request.__name__ = 'request'
        data_set = DataSet.from_group_and_type(
            # bit of a gotcha in the /data here
            'http://dropthebase.com/data',
            'famous-knights',
            'dragons-killed',
            token='token'
        )

        data_set.post({'key': datetime(2012, 12, 12)})

        mock_request.assert_called_with(
            'POST',
            'http://dropthebase.com/data/famous-knights/dragons-killed',
            headers=match_equality(has_entries({
                'Authorization': 'Bearer token',
                'Content-Type': 'application/json',
                'Request-Id': 'Not-Set',
            })),
            data='{"key": "2012-12-12T00:00:00+00:00"}'
        )

    @mock.patch('requests.request')
    def test_post_to_data_set_by_group_and_type_without_bearer_token(
        self, mock_request
    ):
        """ Need to fix the behaviour here """
        raise SkipTest
        mock_request.__name__ = 'request'
        data_set = DataSet.from_group_and_type(
            # bit of a gotcha in the /data here
            'http://dropthebase.com/data',
            'famous-knights',
            'dragons-killed',
        )

        data_set.post({'key': datetime(2012, 12, 12)})

        mock_request.assert_called_with(
            url='http://dropthebase.com/data/famous-knights/dragons-killed',
            headers={
                'Authorization': 'Bearer token',
                'Content-type': 'application/json',
                'Request-Id': 'Not-Set',
            },
            data='{"key": "2012-12-12T00:00:00+00:00"}'
        )

    @mock.patch('requests.request')
    def test_raises_error_on_4XX_or_5XX_responses(self, mock_request):
        mock_request.__name__ = 'request'
        data_set = DataSet('', None)
        response = Response()
        response.status_code = 418
        mock_request.return_value = response
        assert_raises(HTTPError, data_set.post, {'key': 'foo'})

    @mock.patch('requests.request')
    @mock.patch('performanceplatform.client.base.log')
    def test_logs_on_dry_run(self, mock_log, mock_request):
        mock_request.__name__ = 'request'

        data_set = DataSet('', None, dry_run=True)
        data_set.post({'key': datetime(2012, 12, 12)})

        eq_(mock_log.info.call_count, 2)
        eq_(mock_request.call_count, 0)

    @mock.patch('time.sleep')
    @mock.patch('requests.request')
    def test_backs_off_on_bad_gateway(self, mock_request, mock_sleep):
        data_set = DataSet('', None)

        good = Response()
        good.status_code = 200
        good._content = '[]'
        bad = Response()
        bad.status_code = 502

        mock_request.side_effect = [bad, bad, good]
        mock_request.__name__ = 'request'

        # No exception should be raised
        data_set.post([{'key': 'foo'}])

    @mock.patch('time.sleep')
    @mock.patch('requests.request')
    def test_backs_off_on_service_unavailable(self, mock_request, mock_sleep):
        data_set = DataSet('', None)

        good = Response()
        good.status_code = 200
        good._content = '[]'
        bad = Response()
        bad.status_code = 503

        mock_request.side_effect = [bad, bad, good]
        mock_request.__name__ = 'request'

        # No exception should be raised
        data_set.post([{'key': 'foo'}])

    @mock.patch('time.sleep')
    @mock.patch('requests.request')
    def test_does_not_back_off_on_forbidden(self, mock_request, mock_sleep):
        data_set = DataSet('', None)

        good = Response()
        good.status_code = 200
        bad = Response()
        bad.status_code = 403

        mock_request.side_effect = [bad]
        mock_request.__name__ = 'request'

        assert_raises(HTTPError, data_set.post, [{'key': 'foo'}])

    @mock.patch('time.sleep')
    @mock.patch('requests.request')
    def test_fails_after_5_backoffs(self, mock_request, mock_sleep):
        data_set = DataSet('', None)

        bad = Response()
        bad.status_code = 502

        mock_request.return_value = bad
        mock_request.__name__ = 'request'

        assert_raises(HTTPError, data_set.post, [{'key': 'foo'}])
        eq_(mock_request.call_count, 5)

    def test_to_query_string_with_empty(self):
        data_set = DataSet('', None)
        eq_(data_set._to_query_string({}), '')

    def test_to_query_string_with_params(self):
        data_set = DataSet('', None)
        eq_(data_set._to_query_string({
            'foo': 'bar',
            'bar': 'foo'}), '?foo=bar&bar=foo')

    def test_to_query_string_with_param_list(self):
        data_set = DataSet('', None)
        eq_(data_set._to_query_string({
            'foo': ['bar1', 'bar2']}), '?foo=bar1&foo=bar2')

    @mock.patch('requests.request')
    def test_get_data_set_with_params(self, mock_request):
        mock_request.__name__ = 'request'
        data_set = DataSet.from_group_and_type(
            # bit of a gotcha in the /data here
            'http://dropthebase.com/data',
            'famous-knights',
            'dragons-killed',
            token='token',
        )

        data_set.get(query_parameters={'foo': 'bar'})

        mock_request.assert_called_with(
            'GET',
            'http://dropthebase.com/data/'
            'famous-knights/dragons-killed?foo=bar',
            headers=mock.ANY,
            data=mock.ANY,
        )
