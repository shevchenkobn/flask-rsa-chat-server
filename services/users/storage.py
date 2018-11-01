from pyee import EventEmitter

from services.errors import LogicError, ErrorCode
from services.users.model import User

_map = {}


class _Storage(EventEmitter):
    def has(self, name: str):
        return name in _map

    def get(self, name: str):
        user = _map.get(name, None)
        if not user:
            raise LogicError(ErrorCode.AUTH_NO, f'Invalid name {repr(name)}')
        return user

    def add(self, name: str):
        if name in _map:
            raise LogicError(ErrorCode.AUTH_DUPLICATE_NAME)

        user = User(name)
        _map[name] = user
        return user

    def delete(self, name_or_user):
        user = name_or_user \
            if isinstance(name_or_user, User) and name_or_user.name in _map \
            else _map.get(name_or_user, None)
        if not user:
            raise LogicError(ErrorCode.AUTH_NO)

        del _map[user.name]
        self.emit('deleted', user)
        return user


storage = _Storage()
