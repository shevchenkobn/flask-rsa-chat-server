from enum import Enum


class ErrorCode(Enum):
    SERVER = 'SERVER'

    AUTH_NO = 'AUTH_NO'
    AUTH_EMPTY_NAME = 'AUTH_EMPTY_NAME'
    AUTH_DUPLICATE_NAME = 'AUTH_DUPLICATE_NAME'

    KEY_BAD = 'KEY_BAD'
    KEY_SIZE = 'KEY_SIZE'

    # WebSockets only
    MSG_BAD = 'MSG_BAD'


class LogicError(Exception):
    def __init__(self, code, message=None):
        super(LogicError, self).__init__(message)
        if code not in ErrorCode:
            raise ValueError('Code {} is not {}'.format(repr(code), ErrorCode))
        self.__dict__['code'] = code
        if message is not None:
            self.__dict__['message'] = message

    def to_dict(self):
        obj_dict = {
            'code': self.code.value,
        }
        if 'message' in self.__dict__:
            obj_dict['message'] = self.message
        return obj_dict

    def __repr__(self):
        string = f"{self.__class__.__name__}(code={self.code}"
        if 'message' in self.__dict__:
            string += f", message={repr(self.message)}"
        return string + ")"
