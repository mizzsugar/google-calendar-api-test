import pytest
import unittest.mock
import datetime
import event


@unittest.mock.patch('event.ServiceBuilder.renew_token')
@unittest.mock.patch('googleapiclient.discovery.build')
def test_valid_token(mock_build, mock_renew_token):
    credentials = unittest.mock.Mock(valid=True)

    event.ServiceBuilder.build(credentials=credentials)
    assert not mock_renew_token.called

@unittest.mock.patch('event.ServiceBuilder.renew_token')
@unittest.mock.patch('googleapiclient.discovery.build')
def test_expired_token_has_refresh_token(mock_build, mock_renew_token):
    credentials = unittest.mock.Mock(valid=False, expired=True, refresh_token='I am refresh token')

    event.ServiceBuilder.build(credentials=credentials)
    assert  mock_renew_token.called


@unittest.mock.patch('googleapiclient.discovery.Resource')
def test_fetch_events(mock_resource):
    mock_resource.events.return_value.list.return_value.execute.return_value = {
        "items": [
                    {
                        "summary": "test",
                        "start": {
                            "dateTime": "2019-06-03T02:00:00+09:00"
                        },
                        "end": {
                            "dateTime": "2019-06-03T02:45:00+09:00"
                        },
                    },
                        {
                        "summary": "test",
                        "start": {
                            "dateTime": "2019-06-03T02:00:00+09:00"
                        },
                        "end": {
                            "dateTime": "2019-06-03T02:45:00+09:00"
                        },
                    },
        ]
    }
    actual = event.EventManager.fetch_events(number=2, service=mock_resource)
    assert 2 == len(actual)

    for item in actual:
        assert isinstance(item, event.Event)


@unittest.mock.patch('googleapiclient.discovery.Resource')
def test_fetch_no_events(mock_resource):
    mock_resource.events.return_value.list.return_value.execute.return_value = {}

    actual = event.EventManager.fetch_events(number=2, service=mock_resource)
    assert [] == actual
