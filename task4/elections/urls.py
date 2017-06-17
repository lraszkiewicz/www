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
    url(r'^api/obwod/(?P<p_id>[0-9]+)/$', views.place_api, name='place_api'),
    url(r'^api/edytuj_obwod/$', views.edit_place_api, name='edit_place_api'),
    url(r'^api/szukaj/$', views.search_api, name='search_api'),
    url(r'^api/upload_file/(?P<p_id>[0-9]+)$', views.upload_file_api, name='upload_file_api'),
    url(r'^api/delete_file/(?P<f_id>[0-9]+)$', views.delete_file_api, name='delete_file_api')
]
