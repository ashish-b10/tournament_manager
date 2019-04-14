from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import tmdb.routing

channel_routing = [
    # include(tmdb.routing.channel_routing, path=r'^/tmdb/'),
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(tmdb.routing.websocket_urlpatterns)
    ),
})
