import aiohttp
from aiohttp import web

from services import logger
from services.errors import ErrorCode, LogicError
from services.users import User
from ws_api.event_handlers import Emitters, Subscribers


_emitters = Emitters()
_subscribers = Subscribers()
_clients = []


class WSClient(object):
    def __init__(self, ws_response, user):
        if not isinstance(ws_response, web.WebSocketResponse) or \
                not isinstance(user, User):
            raise LogicError(ErrorCode.SERVER)
        self.ws_response = ws_response
        self.user = user

    async def emit(self, event, *args):
        emit = _emitters[event]
        emit(self, *args)

    async def emit_raw(self, event, data):
        await self.ws_response.send_json({
            'event': event,
            'data': data
        })


def event_to_attr(e):
    return e.replace('-', '_')


def attr_to_event(a):
    return a.replace('_', '-')


async def broadcast(event, exclude, *args):
    emit = _emitters[event]
    if not emit:
        raise LogicError(ErrorCode.SERVER)
    broadcast_clients = (c for c in _clients if c not in exclude)

    for client in broadcast_clients:
        emit(client, *args)


async def websocket_handler(request):
    logger.info('\nRequest for WS connect')

    user = request['user']
    if any(client.user.name is user.name for client in _clients):
        # FIXME: check error handler
        raise LogicError(ErrorCode.AUTH_DUPLICATE_NAME)

    ws = web.WebSocketResponse()
    await ws.prepare(request)
    client = WSClient(ws, user)
    _emitters['client-created'](client)
    await broadcast('user-joined', (), client)
    logger.info(f'Client {user.name} connected')
    _clients.append(client)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            logger.info(f'\nMessage from {user.name}')
            try:
                msg_json = msg.json()
            except:
                await ws.send_json(
                    LogicError(ErrorCode.MSG_BAD).to_dict()
                )
                continue
            if not msg_json \
                    or 'event' not in msg_json or isinstance(msg_json['event'], str)\
                    or 'data' not in msg_json:
                await ws.send_json(
                    LogicError(ErrorCode.MSG_BAD).to_dict()
                )
                continue

            logger.info(f'Event {msg_json["event"]}')

            handler = lambda a, b: 9
            try:
                handler(client, msg_json.data)
            except object as err:
                logger.error(f'Error for {user.name}:\nERROR: {err}')
                await ws.send_json(
                    LogicError(ErrorCode.MSG_BAD).to_dict()
                )
        elif msg.type == aiohttp.WSMsgType.ERROR:
            logger.error(f'\nConnection {user.name} is about to close '
                         f'due to {ws.exception()}')

        elif msg.type == aiohttp.WSMsgType.CLOSE:
            _clients.remove(client)
            await broadcast('user-left', (), client)
            _emitters['client-disposed'](client)
            logger.info(f'\nDisonnected {user.name} because of {msg.data} ({msg.extra})')

    return ws

ws_route = web.get('/chat', websocket_handler)
