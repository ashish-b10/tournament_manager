from django.conf.urls import url

from . import views

urlpatterns = [
    #url(r'^$', views.index, name='team'),
    url(r'^match/(?P<match_num>[0-9]+)/$', views.match, name='match'),
    url(r'^$', views.index, name='index'),
]
