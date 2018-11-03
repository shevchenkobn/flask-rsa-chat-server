from copy import deepcopy


_key_bit_size = 2048


class _Config(object):
    def __init__(self, conf_dict):
        self.__dict__ = deepcopy(conf_dict)

    def __getitem__(self, item):
        return self.__dict__[item]

    def to_dict(self):
        return self.__dict__


key_config = _Config(
    {
        'type': 'rsa',
        'padding': 'pkcs1',
        'size': _key_bit_size,
        'expire_time': 10 * 60 * 1000,
        'key_format': {
            'type': 'components',
            'format': {
                'e': {
                    'type': 'integer',
                    'minimum': 0
                },
                'n': {
                    'type': 'array',
                    'items': {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 255
                    },
                    'minItems': _key_bit_size,
                    'maxItems': _key_bit_size
                }
            }
        }
    }
)

jwt_config = _Config(
    {
        'secret': 'This is my rsa server',
        'algo': 'HS256'
    }
)
