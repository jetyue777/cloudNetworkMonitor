from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    # Examples:
    url(r'^main/', 'monitorWebApp.views.main'),
    url(r'^configure/', 'monitorWebApp.views.configure'),
    url(r'^delay/(?P<vm_select>\S+)/', 'monitorWebApp.views.delay'),
    url(r'^delay/$', 'monitorWebApp.views.delay'),
    url(r'^bandwidth/(?P<vm_select>\S+)/', 'monitorWebApp.views.bandwidth'),
    url(r'^bandwidth/$', 'monitorWebApp.views.bandwidth'),

)
