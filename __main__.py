from aiohttp import web
from os import environ

from rest.routes import routes
from rest.middlewares import middlewares
from ws_api import ws_route

app = web.Application(middlewares=middlewares)

app.router.add_routes(routes)
app.router.add_routes([ws_route])

port = environ.get('PORT', 5000)
web.run_app(app, port=port)
