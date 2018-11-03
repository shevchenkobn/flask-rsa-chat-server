from aiohttp import web
import traceback

from services import logger
from services.errors import LogicError, ErrorCode
from services.auth import error_handle_middleware as auth_handler, get_auth_middlewares


@web.middleware
async def error_handler(request, handler):
    try:
        return await handler(request)
    except LogicError as ex:
        response = web.json_response(data=ex.to_dict())
        if ex.code is ErrorCode.AUTH_NO:
            response.set_status(401)
        elif ex.code is ErrorCode.SERVER:
            response.set_status(500)
        else:
            response.set_status(400)
        return response
    except web.HTTPException as ex:
        if ex.status is 404:
            raise ex
        logger.error(f'Unexpected http Error: {repr(traceback.format_exc())}')
        return web.json_response(
            status=ex.status,
            data=LogicError(ErrorCode.SERVER).to_dict()
        )
    except BaseException as ex:
        logger.error(f'Unexpected Error: {repr(traceback.format_exc())}')
        traceback.print_exc()
        return web.json_response(
            status=500,
            data=LogicError(ErrorCode.SERVER).to_dict()
        )


middlewares = (
    error_handler,
    auth_handler,
    *get_auth_middlewares((
        ('POST', '/auth'),
        ('GET', '/status'),
        ('GET', '/key/info'),
    ))
)