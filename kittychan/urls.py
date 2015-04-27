from django.conf.urls import include, url
from django.contrib import admin
from kittymon import views as kittymon_views

urlpatterns = [
    url(r'^', include('kittymon.urls', namespace="kittymon")),
    url(r'^kitties/', include('kittymon.urls', namespace="kittymon")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
]
