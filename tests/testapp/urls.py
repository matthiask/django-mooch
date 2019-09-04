from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


admin.autodiscover()


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('flock.urls')),
]

urlpatterns += staticfiles_urlpatterns()
