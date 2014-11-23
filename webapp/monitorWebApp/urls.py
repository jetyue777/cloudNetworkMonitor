from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    # Examples:
    url(r'^main/', 'monitorWebApp.views.main'),
    url(r'^configure/', 'monitorWebApp.views.configure'),
    url(r'^test/', 'monitorWebApp.views.test'),
   
)
