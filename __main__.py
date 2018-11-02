import asyncio
from aiohttp import web
from os import environ

from rest.routes import routes

loop = asyncio.get_event_loop()
app = web.Application()

app.router.add_routes(routes)
web.run_app(app, port=environ.get('PORT', 5000))
