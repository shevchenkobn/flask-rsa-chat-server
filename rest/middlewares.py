from aiohttp import web

from services import logger
from services.errors import LogicError, ErrorCode
from services.auth import error_handle_middleware as auth_handler, get_auth_middlewares


@web.middleware
async def error_handler(request, handler):
    try:
        return await handler(request)
    except LogicError as ex:
        response = web.HTTPException(body=ex.to_dict())
        if ex.code is ErrorCode.AUTH_NO:
            response.set_status(401)
        elif ex.code is ErrorCode.SERVER:
            response.set_status(500)
        else:
            response.set_status(400)
        raise response
    except web.HTTPException as ex:
        if ex.status is 404:
            raise ex
        logger.error(f'wtf http Error: {repr(ex)}')
        ex.body = LogicError(ErrorCode.SERVER).to_dict()
        raise ex
    except Exception as ex:
        logger.error(f'wtf Error: {repr(ex)}')
        raise web.HTTPServerError(body=LogicError(ErrorCode.SERVER).to_dict())


middlewares = (
    error_handler,
    auth_handler,
    *get_auth_middlewares((
        ('POST', '/auth'),
        ('GET', '/status'),
        ('GET', '/key/info'),
    ))
)