from aiohttp import web

from config import key_config
from services import keys
from services import logger
from services.auth import create_token
from services.errors import LogicError, ErrorCode
from services.users import storage

routes = web.RouteTableDef()


@routes.get('/status')
async def status(request):
    return web.json_response({})


#
# Auth
#

@routes.post('/auth')
async def get_token(request):
    if not request.body_exists:
        raise LogicError(ErrorCode.AUTH_EMPTY_NAME)
    try:
        body = await request.json()
    except:
        raise LogicError(ErrorCode.AUTH_EMPTY_NAME)

    user = storage.add(body['name'])
    token = create_token(user)
    logger.info(f'\nUser {user.name} has token {token}')
    return web.json_response({
        'token': token
    })


@routes.delete('/auth')
async def delete_user(request):
    user = request['user']
    logger.info(f'Deleting token for {user.name}')
    storage.delete(user.name)

    return web.json_response({})


#
# Keys
#


@routes.get('/key/info')
async def key_info(request):
    return web.json_response(key_config.to_dict())


@routes.post('/key')
async def exchange_keys(request):
    logger.info('Key generating')
    if not request.body_exists:
        raise LogicError(ErrorCode.KEY_BAD)
    try:
        body = await request.json()
        components = body['public-key']
    except object as ex:
        logger.info(f'Bad body: {ex}')
        raise LogicError(ErrorCode.KEY_BAD)
    foreign_key = keys.dict_to_public_key(components)

    # TODO: delete keyExpiration and log 'Had keys, deleting'

    private_key, public_key = keys.generate_keys()
    logger.debug(f'myPubK: {public_key.key_size}')
    logger.debug(f'forPubK: {foreign_key.key_size}')

    user = request['user']
    user.update_keys(private_key, public_key)

    return web.json_response({
        'public-key': keys.public_key_to_dict(public_key)
    })
