from django.conf.urls.defaults import *
from django.contrib.auth.models import User
from django.contrib.auth.views  import login
from projects.models import *
import projects

urlpatterns = patterns('projects.views',
    (r'^(?P<account>[-\w]+)/projects/$', 'index'),
    (r'^(?P<account>[-\w]+)/projects/(?P<project_id>\d+)/$', 'project_detail'),
    (r'^(?P<account>[-\w]+)/projects/(?P<project_id>\d+)/delete/$', 'delete_project'),
    (r'^(?P<account>[-\w]+)/projects/(?P<project_id>\d+)/edit/$', 'edit_project'),

    (r'^(?P<account>[-\w]+)/companies/$', 'company_list'),

    (r'^(?P<account>[-\w]+)/people/(?P<user_id>\d+)/$', 'people_detail'),
    (r'^(?P<account>[-\w]+)/people/(?P<user_id>\d+)/edit/$', 'edit_profile'),
    
    # User Invitation
    (r'^(?P<account>[-\w]+)/companies/(?P<company_id>\d+)/people/new/$', 'invite'),
    (r'^(?P<account>[-\w]+)/invitation/(?P<code>\w+)/$', 'invite_accept'),
    (r'^(?P<account>[-\w]+)/new_user/$', 'invite_join'),

    (r'^(?P<account>[-\w]+)/companies/new/$', 'new_company'),

    # Canvas Sets
        
    # All your different canvases (the important stuff)
    (r'^(?P<account>[-\w]+)/projects/(?P<project_id>\d+)/canvases/$', 'canvas_set_list'),
    (r'^(?P<account>[-\w]+)/projects/(?P<project_id>\d+)/canvases/tag/(?P<tag>[^/]+)/$','with_tag'), 
    # See all versions of a canvas
    url(r'^(?P<account>[-\w]+)/projects/(?P<project_id>\d+)/canvases/(?P<canvas_set_id>\d+)/$', 'canvas_set_detail', name="canvas_set_detail"),
    (r'^(?P<account>[-\w]+)/projects/(?P<project_id>\d+)/canvases/(?P<canvas_set_id>\d+)/subscription/$', 'subscribe_canvas_updates'),
    
    # One specific canvas
    (r'^(?P<account>[-\w]+)/projects/(?P<project_id>\d+)/canvases/(?P<canvas_set_id>\d+)/v/(?P<canvas_version>\d+)/$', 'canvas_detail'),

    # Updates
    (r'^(?P<account>[-\w]+)/projects/(?P<project_id>\d+)/updates/$', 'update_list'),
    url(r'^(?P<account>[-\w]+)/projects/(?P<project_id>\d+)/updates/(?P<update_id>\d+)/$', 'update_detail', name="update_detail"),
    (r'^(?P<account>[-\w]+)/projects/(?P<project_id>\d+)/updates/(?P<update_id>\d+)/subscription/$', 'subscribe_update_updates'),
    
    # Form Views
    (r'^(?P<account>[-\w]+)/projects/new/$', 'project_new'),
    (r'^(?P<account>[-\w]+)/projects/(?P<project_id>\d+)/updates/new/$', 'update_new'),

    # Add a new canvas to an existing Canvas Set
    (r'^(?P<account>[-\w]+)/projects/(?P<project_id>\d+)/canvases/(?P<canvas_set_id>\d+)/v/(?P<canvas_version>\d+)/new/$', 'canvas_add'),
    (r'^(?P<account>[-\w]+)/projects/(?P<project_id>\d+)/canvases/(?P<canvas_set_id>\d+)/new/$', 'canvas_add'),
        
    #This view creates a new canvas set, and a new canvas.
    (r'^(?P<account>[-\w]+)/projects/(?P<project_id>\d+)/canvases/new/$', 'canvas_new'),
    
    (r'^save_canvas/$', 'save_new_canvas'),
    (r'^save_add_canvas/$', 'save_add_canvas'),
    
    # Site Admin
    (r'^(?P<account>[-\w]+)/settings/$', 'settings'),
    (r'^(?P<account>[-\w]+)/account/$', 'account'),
    (r'^add_account/$', 'account_add'),
    (r'^(?P<account>[-\w]+)/$', 'index'),
)