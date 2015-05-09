import requests
import logging


class Runscope(object):
    """Class for querying the Runscope API"""
    def __init__(self, auth_key):
        """Sets our base URL and stores our auth_key for later"""
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
        """Logs any errors and then returns None for data"""
        if response['error']:
            logging.error('API Error: %s', response['error'])
            return None
        else:
            return response.get('data', [])

    def get_buckets(self):
        """Gets a list of all buckets in the account"""
        return self.make_request('buckets')

    def get_bucket_messages(self, bucket_id=None, since=None, count=None):
        """Gets the requested messages by bucket_id"""
        endpoint = 'buckets/%s/messages' % (bucket_id)
        params = {}
        if since:
            params['since'] = since
        if count:
            params['count'] = count
        return self.make_request(endpoint, params=params)
