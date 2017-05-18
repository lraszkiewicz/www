from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^api/login/$', views.login_api, name='login_api'),
    url(r'^api/logout/$', views.logout_api, name='logout_api'),
    url(r'^api/kraj/$', views.country_api, name='country_api'),
    url(r'^api/wojewodztwo/(?P<v_id>[0-9]+)/$', views.voivodeship_api, name='voivodeship_api'),
    url(r'^api/okreg/(?P<d_id>[0-9]+)/$', views.district_api, name='district_api'),
    url(r'^api/gmina/(?P<m_id>[0-9]+)/$', views.municipality_api, name='municipality_api'),
    url(r'^obwod/(?P<p_id>[0-9]+)/$', views.place, name='place'),
    url(r'^api/szukaj/$', views.search_api, name='search_api'),
    url(r'^delete_file/(?P<f_id>[0-9]+)$', views.delete_file, name='delete_file')
]
