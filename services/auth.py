import jwt
from aiohttp import web
from aiohttp_jwt import JWTMiddleware

from config import jwt_config
from services.errors import LogicError, ErrorCode
import services.logger as logger
from services.users.model import User
from services.users import storage


class Payload(object):
    def __init__(self, user):
        if hasattr(user, 'name') and isinstance(user.name, str):
            raise LogicError(ErrorCode.SERVER, f'{repr(user)} not a User!')
        self.id = user.name

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def is_valid(o):
        return hasattr(o, 'id') and isinstance(o.id, str)


def create_token(user: User):
    return jwt.encode(Payload(user).to_dict(), jwt_config.secret, algorithm=jwt_config.algo)


def get_user_from_payload(o):
    if not Payload.is_valid(o):
        raise LogicError(ErrorCode.AUTH_NO)
    name = o.id
    return storage[name]


_jwt_check = JWTMiddleware(
    secret_or_pub_key=jwt_config.secret,
    algorithms=[jwt_config.algo]
)


def get_auth_middlewares(noauth_routes):
    @web.middleware
    async def prechecker(request, handler):
        if (request.method, request.path,) in noauth_routes:
            return await handler(request)
        else:
            return await _jwt_check(request, handler)

    @web.middleware
    async def payload_handler(request, handler):
        payload = request['payload']
        if not Payload.is_valid(payload):
            raise web.HTTPForbidden(reason='Invalid user')
        del request['payload']
        request['user'] = storage[payload.id]
        logger.log(f'User: {payload.id}')
        return await handler(request)

    return (
        prechecker,
        payload_handler
    )


@web.middleware
def error_handle_middleware(request, handler):
    try:
        return await handler(request)
    except web.HTTPException as ex:
        logger.error(ex)
        if ex.status in (401, 403):
            return web.json_response(
                status=ex.status,
                body=LogicError(ErrorCode.AUTH_NO, ex.reason).to_dict()
            )
        raise ex
    except LogicError as ex:
        logger.error(ex)
        if ex.code is ErrorCode.AUTH_NO:
            return web.json_response(
                status=403,
                body=ex.to_dict()
            )
        raise ex


def _get_jwt_payload(request):
    try:
        _jwt_check(request, lambda request: request)
    except web.HTTPException as ex:
        logger.error(ex)
        return None
    payload = request['payload']
    del request['payload']
    return payload


def get_user_from_request(request):
    payload = _get_jwt_payload(request)

    if Payload.is_valid(payload):
        return storage[payload.id]

    raise LogicError(ErrorCode.AUTH_NO)
