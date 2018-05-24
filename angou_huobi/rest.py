from urllib.parse import urlencode
import logging
import requests
from . import auth_utils


LOGGER = logging.getLogger('angou_huobi')


_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'


class InvalidJSON(Exception):
    pass


class RestError(Exception):
    def __init__(self, code, message):
        super().__init__(f'[{code}] {message}')
        self.code = code
        self.message = message


class RestSession:
    def __init__(self, api_key, api_secret, domain='api.huobi.pro', lang='en', timeout=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.domain = domain
        self.lang = lang
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            'Accept': 'application/json',
            'User-Agent': _USER_AGENT,
            'Accept-Language': self.lang,
        })

    @staticmethod
    def _postprocess(r):
        r.raise_for_status()
        try:
            resp = r.json()
        except ValueError:
            raise InvalidJSON()
        try:
            if resp['status'] == 'error':
                raise RestError(resp['err-code'], resp['err-msg'])
            return resp['data']
        except KeyError:
            raise InvalidJSON()

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
        LOGGER.debug('GET %s signed=%s params=%s', path, signed, params)

        if signed:
            params = params or {}
            self._add_auth_params('GET', path, params)

        return self._postprocess(self._session.request(
            'GET', f'https://{self.domain}{path}', params=params, timeout=self.timeout))

    def post(self, path, signed=False, params=None):
        LOGGER.debug('POST %s signed=%s params=%s', path, signed, params)

        query = None
        if signed:
            query = {}
            self._add_auth_params('POST', path, query)

        return self._postprocess(self._session.request(
            'POST', f'https://{self.domain}{path}', json=params, params=query,
            timeout=self.timeout))
