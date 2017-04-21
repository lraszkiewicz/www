from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^wojewodztwo/[a-z\-]*(?P<v_id>[0-9]+)/$', views.voivodeship, name='voivodeship'),
    url(r'^okreg/(?P<d_id>[0-9]+)/$', views.district, name='district'),
    url(r'^gmina/[a-z\-]*(?P<m_id>[0-9]+)/$', views.municipality, name='municipality'),
    url(r'^obwod/(?P<p_id>[0-9]+)/$', views.place, name='place'),
    url(r'^search/$', views.search, name='search'),
]
