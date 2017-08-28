from django.conf.urls import url
from . import views
from .import admin

urlpatterns = [
    url(r'^$', views.showberanda, name='showberanda'),
    url(r'^sentimenanalisis/$', views.showsentimenanalisis, name='showsentimenanalisis'),
    url(r'^bantuan/$', views.showbantuan, name='showbantuan'),
    url(r'^tweets/', views.get_tweets),
]