from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^wojewodztwo/.*$', views.voivodeship, name='voivodeship'),
    url(r'^api/wojewodztwo/[a-z\-]*(?P<v_id>[0-9]+)/$', views.voivodeship_api, name='voivodeship_api'),
    url(r'^okreg/.*$', views.district, name='district'),
    url(r'^api/okreg/(?P<d_id>[0-9]+)/$', views.district_api, name='district_api'),
    url(r'^gmina/.*$', views.municipality, name='municipality'),
    url(r'^api/gmina/(?P<m_id>[0-9]+)/$', views.municipality_api, name='municipality_api'),
    url(r'^obwod/(?P<p_id>[0-9]+)/$', views.place, name='place'),
    url(r'^search/$', views.search, name='search'),
    url(r'^delete_file/(?P<f_id>[0-9]+)$', views.delete_file, name='delete_file')
]
