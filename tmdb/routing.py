from channels.routing import route

from . import consumers
from . import urls

channel_routing = [
    route("websocket.connect", consumers.match_updates_connect,
            path=urls.tournament_base + r'/match_updates/*$'),
    route("websocket.receive", consumers.match_updates_message,
            path=urls.tournament_base + r'/match_updates/*$'),
    route("websocket.disconnect", consumers.match_updates_disconnect),
]
