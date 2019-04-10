from channels.routing import ProtocolTypeRouter

# import tmdb.routing

channel_routing = [
    # include(tmdb.routing.channel_routing, path=r'^/tmdb/'),
]

application = ProtocolTypeRouter({
})
