from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^match/(?P<match_num>[0-9]+)/*$', views.match, name='match'),
    url(r'^rings/*$', views.rings, name='rings'),
    url(r'^division/(?P<division_id>[0-9]+)/*$', views.division,
            name='division'),
    url(r'^division/*$', views.division, name='division'),
    url(r'^$', views.index, name='index'),
]
