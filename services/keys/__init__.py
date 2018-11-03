from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

from config import key_config
from services.errors import ErrorCode, LogicError
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
    debug(f'len - {len(byte_seq)}; chunk - {chunk_size}')
    for i in range(0, len(byte_seq), chunk_size):
        debug(f'{i} - ${i + chunk_size}')
        bytes_list.append(
            public_key.encrypt(
                byte_seq[i:i + chunk_size],
                _default_padding()
            )
        )
    return b''.join(bytes_list)


def decrypt(private_key, byte_seq):
    chunk_size = _chunk_sizes['decrypt']
    bytes_list = []
    debug(f'len - {len(byte_seq)}; chunk - {chunk_size}')
    for i in range(0, len(byte_seq), chunk_size):
        debug(f'{i} - {i + chunk_size}')
        debug(byte_seq[i:i + chunk_size])
        bytes_list.append(
            private_key.decrypt(
                byte_seq[i:i + chunk_size],
                _default_padding()
            )
        )
    return b''.join(bytes_list)


def is_dict_valid_pbk(d):
    return 'e' in d and 'n' in d \
           and hasattr(d['n'], '__iter__') and isinstance(d['e'], int)


def dict_to_public_key(d):
    if not is_dict_valid_pbk(d):
        raise LogicError(ErrorCode.KEY_BAD)
    if len(d['n']) is not (key_config.size + 7) // 8:
        raise LogicError(ErrorCode.KEY_SIZE)

    try:
        n = int.from_bytes(bytes(i for i in d['n']), 'big')
        return rsa.RSAPublicNumbers(d['e'], n).public_key(default_backend())
    except:
        raise LogicError(ErrorCode.KEY_BAD)


def public_key_to_dict(pbk):
    public_numbers = pbk.public_numbers()
    n = public_numbers.n
    int_tuple = tuple(i for i in n.to_bytes((n.bit_length() + 7) // 8, 'big'))
    d = {
        'n': int_tuple,
        'e': public_numbers.e,
    }
    debug(d)
    return {
        'n': int_tuple,
        'e': public_numbers.e,
    }
