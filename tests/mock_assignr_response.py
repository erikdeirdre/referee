from unittest import mock

def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    valid_response = {
        'page': {'records': 1, 'pages': 1, 'current_page': 1, 'limit': 200},
        '_embedded': {
            'availability': [{
                'id': 123, 'date': '2023-01-01', 'all_day': True, 'description': 'all day', 'created': '2023-10-05T21:24:22.000-04:00', 'updated': '2023-10-05T21:24:22.000-04:00'
            }]
        }
    }
    invalid_response = {
        'page': {'records': 1, 'pages': 1, 'current_page': 1, 'limit': 200},
        '_embedded': {
        }
    }

    if args[0] == 'http://test.com/api/v2/users/test/availability':
        return MockResponse(valid_response, 200)
    elif args[0] == 'http://fail.com/api/v2/users/test/availability':
        return MockResponse(invalid_response, 200)
    elif args[0] == 'http://test.com/api/v2/users/invaliduser/availability':
        return MockResponse(invalid_response, 200)
    return MockResponse(None, 404)

def mocked_requests_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'http://test.com/oauth/valid':
        return MockResponse({"access_token": "validtoken"}, 200)
    elif args[0] == 'http://test.com/oauth/invalid':
        return MockResponse({"no_token": "no token"}, 200)

    return MockResponse(None, 404)
