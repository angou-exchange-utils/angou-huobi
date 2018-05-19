from urllib.parse import urlencode
import logging
import requests
from . import auth_utils


_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'


class RestError(Exception):
    def __init__(self, code, message):
        super().__init__(f'[{code}] {message}')
        self.code = code
        self.message = message


class RestSession:
    def __init__(self, api_key, api_secret, domain='api.huobi.pro', lang='en'):
        self.api_key = api_key
        self.api_secret = api_secret
        self.domain = domain
        self.lang = lang
        self._session = requests.Session()
        self._session.headers.update({
            'Accept': 'application/json',
            'User-Agent': _USER_AGENT,
            'Accept-Language': self.lang,
        })
        self.logger = logging.getLogger('angou_huobi')

    def _postprocess(self, req):
        r = self._session.send(self._session.prepare_request(req))
        r.raise_for_status()
        resp = r.json()
        if resp['status'] == 'error':
            raise RestError(resp.get('err-code', ''), resp.get('err-msg', ''))
        return resp['data']

    def _get(self, url, params=None):
        return self._postprocess(requests.Request('GET', url, params=params))

    def _post(self, url, params=None, query=None):
        return self._postprocess(requests.Request('POST', url, json=params, params=query, headers={
            'Content-Type': 'application/json',
        }))

    def _add_auth_params(self, verb, path, params):
        params.update({
            'AccessKeyId': self.api_key,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': '2',
            'Timestamp': auth_utils.generate_timestamp(),
        })
        encoded_params = urlencode(sorted(params.items(), key=lambda kv: kv[0]))
        payload = '\n'.join((verb, self.domain, path, encoded_params))
        params['Signature'] = auth_utils.generate_signature(self.api_secret, payload)

    def get(self, path, signed=False, params=None):
        self.logger.debug('GET %s signed=%s params=%s', path, signed, params)
        if signed:
            params = params or {}
            self._add_auth_params('GET', path, params)
        return self._get(f'https://{self.domain}{path}', params)

    def post(self, path, signed=False, params=None):
        self.logger.debug('POST %s signed=%s params=%s', path, signed, params)
        url = f'https://{self.domain}{path}'
        query = None
        if signed:
            query = {}
            self._add_auth_params('POST', path, query)
        return self._post(url, params, query)
