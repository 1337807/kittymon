from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'kittychan.views.home', name='home'),
    url(r'^kitties/', include('kittymon.urls', namespace="kittymon")),
    url(r'^admin/', include(admin.site.urls)),
]
