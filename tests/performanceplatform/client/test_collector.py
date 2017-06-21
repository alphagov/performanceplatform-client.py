from hamcrest import match_equality, has_entries
from mock import patch
from performanceplatform.client.collector import CollectorAPI


class TestCollectorAPI(object):
    @patch('requests.request')
    def test_get_collector_type(self, mock_request):
        mock_request.__name__ = 'request'
        api = CollectorAPI('http://collector.api', 'token')
        api.get_collector_type('foo-type')

        mock_request.assert_called_with(
            method='GET',
            url='http://collector.api/collector-type/foo-type',
            headers=match_equality(has_entries({
                'Accept': 'application/json',
                'Authorization': 'Bearer token'
            })),
            data=None,
            params=None,
        )

    @patch('requests.request')
    def test_list_collector_types(self, mock_request):
        mock_request.__name__ = 'request'
        api = CollectorAPI('http://collector.api', 'token')
        api.list_collector_types()

        mock_request.assert_called_with(
            method='GET',
            url='http://collector.api/collector-type',
            headers=match_equality(has_entries({
                'Accept': 'application/json',
                'Authorization': 'Bearer token'
            })),
            data=None,
            params=None,
        )

    @patch('requests.request')
    def test_get_collector(self, mock_request):
        mock_request.__name__ = 'request'
        api = CollectorAPI('http://collector.api', 'token')
        api.get_collector('foo')

        mock_request.assert_called_with(
            method='GET',
            url='http://collector.api/collector/foo',
            headers=match_equality(has_entries({
                'Accept': 'application/json',
                'Authorization': 'Bearer token'
            })),
            data=None,
            params=None,
        )

    @patch('requests.request')
    def test_list_collectors(self, mock_request):
        mock_request.__name__ = 'request'
        api = CollectorAPI('http://collector.api', 'token')
        api.list_collectors()

        mock_request.assert_called_with(
            method='GET',
            url='http://collector.api/collector',
            headers=match_equality(has_entries({
                'Accept': 'application/json',
                'Authorization': 'Bearer token'
            })),
            data=None,
            params=None,
        )
