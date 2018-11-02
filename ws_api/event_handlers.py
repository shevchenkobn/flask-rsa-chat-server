from services import logger
from services.errors import LogicError, ErrorCode
from services.keys import encrypt, decrypt
from ws_api import event_to_attr, broadcast


class _EventHandlers(object):
    def __getitem__(self, event):
        return self.__dict__.get(event_to_attr(event), None)


class Subscribers(_EventHandlers):
    async def message_sent(self, client, payload):
        # FIXME: check type of message
        if not isinstance(payload, dict)\
                or 'message' not in payload or '__iter__' not in payload['message']:
            logger.error('Ill-formed message')
            client.emit('error', LogicError(ErrorCode.MSG_BAD).to_dict())
            return

        try:
            src_bytes = bytes(i for i in payload['message'])
        except:
            client.emit('error', LogicError(ErrorCode.MSG_BAD).to_dict())
            return

        msg_bytes = decrypt(client.user.decrypt_key, src_bytes)
        logger.debug(str(msg_bytes))
        await broadcast('message-received', [], msg_bytes, client.user.name)


class Emitters(_EventHandlers):
    async def message_received(self, client, msg_bytes, username):
        encrypted = encrypt(client.user.encrypt_key, msg_bytes)
        await client.emit_raw('message-received', {
            'username': username,
            'message': (i for i in encrypted)
        })

    async def client_created(self, client):
        async def callback(err):
            if err:
                await client.emit('error', err)
            else:
                await client.emit_raw('key-outdated', {})

        # TODO: check if has expiration and update it, else - create it

    async def user_joined(self, curr_client, new_client):
        await curr_client.emit_raw('user-joined', {
            'username': new_client.user.name
        })

    async def user_left(self, curr_client, old_client):
        await curr_client.emit_raw('user-left', {
            'username': old_client.user.name
        })

    async def client_disposed(self, client):
        # TODO: delete expiration callback
        pass

    async def error(self, client, err):
        logger.error(err)
        err = err if isinstance(err, LogicError) else LogicError(ErrorCode.SERVER)
        client.emit_raw('raw', err.to_dict())
