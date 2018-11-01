from services.utils import utc_ms
from services.errors import LogicError, ErrorCode


class User(object):
    def __init__(self, name, encrypt_key=None, decrypt_key=None):
        if not isinstance(name, str) or name.strip():
            raise LogicError(ErrorCode.AUTH_EMPTY_NAME)
        if not (isinstance(encrypt_key, (str, bytes)) or encrypt_key is None)\
                or (not isinstance(decrypt_key, (str, bytes)) or decrypt_key is None):
            raise LogicError(ErrorCode.SERVER, f'Bad key type: '
                                               f'encrypt - {repr(encrypt_key)}, decrypt - {repr(decrypt_key)}')
        self._name = name
        self._encrypt_key = encrypt_key
        self._decrypt_key = decrypt_key
        self._updated_at = utc_ms()
        self._last_logged_in = self._updated_at

        @property
        def name(self):
            return self._name

        @property
        def encrypt_key(self):
            return self._encrypt_key

        @property
        def decrypt_key(self):
            return self._decrypt_key

        @property
        def updated_at(self):
            return self._updated_at

        @property
        def last_logged_in(self):
            return self._last_logged_in

        def has_keys():
            return encrypt_key and decrypt_key

        def update_keys(encrypt_key: bytes, decrypt_key: bytes):
            if not isinstance(encrypt_key, (str, bytes)) or not encrypt_key:
                raise LogicError(ErrorCode.KEY_BAD, 'Bad encrypt key')
            if not isinstance(decrypt_key, (str, bytes)) or not decrypt_key:
                raise LogicError(ErrorCode.KEY_BAD, 'Bad decrypt key')

            self._encrypt_key = encrypt_key
            self._decrypt_key = decrypt_key
            self._updated_at = utc_ms()

            return self._updated_at

        def delete_keys(self):
            self._encrypt_key = None
            self._decrypt_key = None
            self._updated_at = utc_ms()

            return self._updated_at

        def log_in(self):
            self._last_logged_in = utc_ms()
            return self._last_logged_in
