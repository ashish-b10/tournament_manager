from channels import include

import tmdb.routing

channel_routing = [
    include(tmdb.routing.channel_routing, path=r'^/tmdb/'),
]
