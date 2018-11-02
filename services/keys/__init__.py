from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

from config import key_config
from services.logger import debug


_e = 65537


_default_padding = padding.PKCS1v15


_RSA_PADDING = {
    'encrypt': 11,
    'decrypt': 0
}


def _get_chunk_size(key_bits, type):
    size = key_bits // 8
    return size - _RSA_PADDING[type]


_chunk_sizes = {
    'encrypt': _get_chunk_size(key_config.size, 'encrypt'),
    'decrypt': _get_chunk_size(key_config.size, 'decrypt'),
}
debug(_chunk_sizes)


def generate_keys():
    private_key = rsa.generate_private_key(_e, key_config.size, default_backend())
    public_key = private_key.public_key()
    return private_key, public_key


def encrypt(public_key, byte_seq):
    chunk_size = _chunk_sizes['encrypt']
    bytes_list = []
    debug(len(byte_seq), chunk_size)
    for i in range(0, len(byte_seq), chunk_size):
        debug(f'{i} - ${i + chunk_size}')
        bytes_list.append(
            public_key.encrypt(
                byte_seq[i:i + chunk_size],
                _default_padding
            )
        )
    return b''.join(bytes_list)


def decrypt(private_key, byte_seq):
    chunk_size = _chunk_sizes['decrypt']
    bytes_list = []
    debug(len(byte_seq), chunk_size)
    for i in range(0, len(byte_seq), chunk_size):
        debug(f'{i} - ${i + chunk_size}')
        bytes_list.append(
            private_key.decrypt(
                byte_seq[i:i + chunk_size],
                _default_padding
            )
        )
    return b''.join(bytes_list)


def save_keys_for_user(username_or_user, decrypt_key, encrypt_key):
    raise Exception("mustn't be used, just save fucking instances or add utils for encrypt key creation from user")
