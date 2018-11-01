from aiohttp import web

routes = (
    web.RouteDef('GET', '/status', lambda request: web.json_response({}), kwargs={}),
)
