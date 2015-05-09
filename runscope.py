import requests
import logging


class Runscope(object):
    def __init__(self, auth_key):
        self.base_url = 'https://api.runscope.com/'
        self.auth_key = auth_key

    def make_request(self, endpoint, params=None):
        """Adds our auth header and requests the data
        """
        headers = {'Authorization': 'Bearer %s' % (self.auth_key)}
        url = self.base_url + endpoint
        r = requests.get(url, headers=headers, params=params)
        return self.get_data(r.json())

    def get_data(self, response):
        if response['error']:
            logging.error('API Error: %s', response['error'])
            return None
        else:
            return response.get('data', [])

    def get_buckets(self):
        return self.make_request('buckets')

    def get_bucket_messages(self, bucket_id=None, since=None, count=None):
        endpoint = 'buckets/%s/messages' % (bucket_id)
        params = {}
        if since:
            params['since'] = since
        if count:
            params['count'] = count
        return self.make_request(endpoint, params=params)
