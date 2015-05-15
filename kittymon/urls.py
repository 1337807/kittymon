from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^catch$', views.CatchView.as_view(), name='catch'),
    url(r'^caught$', views.caught, name='caught'),
    url(r'^fight/(?P<hero_userkitty_id>[0-9]+)/(?P<villain_userkitty_id>[0-9]+)$', views.fight, name='fight'),
    url(r'^register$', views.register, name='register'),
]
