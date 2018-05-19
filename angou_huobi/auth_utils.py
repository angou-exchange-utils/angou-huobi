import hmac
import hashlib
import base64
import datetime


def generate_signature(secret, payload):
    if not isinstance(payload, (bytes, bytearray)):
        payload = payload.encode('utf8')
    digest = hmac.new(secret.encode('utf8'), payload, digestmod=hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


def generate_timestamp():
    return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
