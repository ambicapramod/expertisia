from django.conf.urls import url
from .views import *
from django.views.generic import TemplateView
urlpatterns = [
	url(r'^$',search_form,name='search_form'),
	url(r'^search/',search_query,name='search_query'),
	url(r'^api/data/$', get_data, name='api-data'),
	url(r'^api/chart/data/$', ChartData.as_view()),
]
