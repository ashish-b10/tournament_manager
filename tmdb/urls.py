from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
    url(r'^match/(?P<match_num>[0-9]+)/*$', views.match, name='match'),
    url(r'^rings/*$', views.rings, name='rings'),
    url(r'^teams/(?P<division_id>[0-9]+)/*$', views.team_list,
            name='team_list'),
    url(r'^teams/*$', views.team_list,
            name='team_list'),
    url(r'^matches/(?P<division_id>[0-9]+)/*$', views.match_list,
            name='match_list'),
    url(r'^matches/*$', views.match_list, name='match_list'),
    url(r'^seedings/(?P<division_id>[0-9]+)/*$', views.seedings,
            name='seedings'),
    url(r'^$', views.index, name='index'),
]

urlpatterns += staticfiles_urlpatterns()
