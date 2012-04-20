from django.conf.urls.defaults import *
from django.contrib import databrowse
from django.contrib.auth.views import login
from projects.models import *
from django.contrib import admin
import settings
admin.autodiscover()

databrowse.site.register(Project)
databrowse.site.register(Update)
databrowse.site.register(UpdateComment)
databrowse.site.register(Canvas)
databrowse.site.register(CanvasField)
databrowse.site.register(CanvasComment)
databrowse.site.register(Action)
databrowse.site.register(Company)
databrowse.site.register(Account)

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    #(r'^databrowse/(.*)', databrowse.site.root),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.apps_path + '/public/'}),
    #(r'^accounts/', include('registration.backends.default.urls')),
    (r'^signup/$', 'projects.views.account_new'),
    (r'^logout/$', 'projects.views.logout_view'),
    (r'^login/$', login),
    
    
    (r'', include('projects.urls')),
    (r'^(?P<account>[-\w]+)/$', 'projects.views.index'),
    (r'^$', 'projects.views.home'),
)
