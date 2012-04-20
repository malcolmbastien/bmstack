from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.template import Context
from django.template.loader import get_template
from django.utils.timesince import timesince as timesince_
from projects.signals import action
from datetime import datetime  
import settings
import string
import smtplib
import tagging
from tagging.fields import TagField

CANVAS_TYPE = (
    ('P', 'Photo'),
    ('W', 'Web'),
)

IM_SERVICE = (
    ('SK', 'Skype'),
    ('AO', 'AOL'),
    ('MS', 'MSN'),
    ('IC', 'ICQ'),
    ('YA', 'Yahoo'),
    ('JA', 'Jabber'),
    ('GO', 'Google'),
)

CANVAS_COLOUR = (
    ('or', 'Orange'),
    ('bl', 'Blue'),
    ('yl', 'Yellow')
)

CANVAS_BLOCK = (
    ('cs', 'Customer Segments'),
    ('cr', 'Customer Relationships'),
    ('ch', 'Channels'),
    ('vp', 'Value Proposition'),
    ('ka', 'Key Activities'),
    ('kr', 'Key Resources'),
    ('kp', 'Key Partners'),
    ('co', 'Cost Structure'),
    ('rs', 'Revenue Streams'),
)

class Account(models.Model):
    #Account is the url address account.bmstack.com
    account = models.CharField(max_length=60, unique=True)
    #Site Name is the Readable account label
    site_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
#    billing_info

    def __str__(self):
        #Passing account because this is what forms urls
        return self.account
        
    def get_absolute_url(self):
        return "http://bmstack.com/%s" % self.account
        
    def save(self, *args, **kwargs):
        self.account = self.account.lower()
        super(Account, self).save(*args, **kwargs)

class Company(models.Model):
    account = models.ForeignKey(Account)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=75, blank=True)
    address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=80, blank=True)
    state = models.CharField(max_length=80, blank=True)
    postal_code = models.CharField(max_length=6, blank=True)
    #country = models.CharField(max_length=2, choices=Country)
    web_address = models.URLField(blank=True)
    office = models.CharField(max_length=20, blank=True)
    fax = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    #Prime company is the one that's associated with an Account. They have more permissions.
    prime = models.BooleanField()
    
    def __str__(self):
        return self.name
        
class UserProfile(models.Model):
    user = models.ForeignKey(User)
    profile_image_key = models.IntegerField(null=True, blank=True)
    
    @property
    def profile_image(self):
        if self.profile_image_key == '' or self.profile_image_key == None:
            # This method isn't being used because its still a WIP. Make it work!
            import urllib, hashlib
            size = 100
            #default = "http://" + settings.DOMAIN_NAME + "/images/avatar.jpg"
            default = settings.DOMAIN_NAME + "/images/avatar.jpg"

            gravatar_url = "http://www.gravatar.com/avatar.php?"
            gravatar_url += urllib.urlencode({'gravatar_id':hashlib.md5(self.user.email).hexdigest(), 
                'default':default, 'size':str(size)})
            return gravatar_url
        else:
            return 'http://' + settings.AWS_BUCKET_URL + '/' + self.profile_image_key + '.jpg'
            
    def get_edit_url(self):
        account_user = AccountUser.objects.get(user=self.user)
        return "/%s/people/%i/edit/" % (account_user.account, self.user.id)
        
    def is_prime_company(self):
        account_user = AccountUser.objects.get(user=self.user)
        return account_user.company.prime
    
    def __str__(self):
        return self.user
        

class AccountUser(models.Model):
    account = models.ForeignKey(Account)
    user = models.ForeignKey(User)
    company = models.ForeignKey(Company)
    title = models.CharField(max_length=100, blank=True)
    #Account specific email
    email = models.EmailField(max_length=75, blank=True)
    office = models.CharField(max_length=20, blank=True)
    office_ext = models.SmallIntegerField(blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True)
    fax = models.CharField(max_length=20, blank=True)
    home = models.CharField(max_length=20, blank=True)
    im_name = models.CharField(max_length=100, blank=True)
    im_service = models.CharField(max_length=2, choices=IM_SERVICE, blank=True)
    automatic_access = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        name = (self.account.account, ' ',self.user.username,)
        return ''.join(name)
    
    def get_absolute_url(self):
        return "/%s/people/%i" % (self.account.account, self.id)
        
class Project(models.Model):
    name = models.CharField(max_length=60)
    account = models.ForeignKey(Account)
    user = models.ForeignKey(User)
    note = models.TextField(blank=True)
    
    companies = models.ManyToManyField(Company)
    status = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def send_project(self, actor, verb, target, created_at, project, company, private_action):
        return action.send(sender=self, actor=actor, verb=verb, target=target, created_at=created_at, project=project, company=company, private_action=private_action)
        
    def get_canvas_count(self):
        return CanvasSet.objects.filter(project=self).count()

    def get_update_count(self):
        return Update.objects.filter(project=self).count()
    
    def __str__(self):
        return self.name
        
    def get_absolute_url(self):
        return "/%s/projects/%i" % (self.account, self.id)
    
    def get_edit_url(self):
        return "/%s/projects/%i/edit" % (self.account, self.id)

class Update(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)
    private_update = models.BooleanField(default=False)
    title = models.CharField(max_length=140)
    update = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def send_update(self, actor, verb, target, created_at, project, company, private_action):
        return action.send(sender=self, actor=actor, verb=verb, target=target, created_at=created_at, project=project, company=company, private_action=private_action)
        
    def get_absolute_url(self):
        return "/%s/projects/%i/updates/%i/" % (self.project.account, self.project.id, self.id)
        
    def __str__(self):
        return self.title
        
    def send_update_email(self, name, email, comment):
        subject = u'New comments added'
        link = 'http://%s/%s/projects/%i/updates/%i/#comment-%i' % (settings.SITE_HOST, self.project.account, self.project.id, self.id, comment.id)
        settings_link = 'http://%s/%s/projects/%i/updates/%i/' % (settings.SITE_HOST, self.project.account, self.project.id, self.id)
        template = get_template('projects/update_email.txt')
        context = Context({'name':name, 'update':self.title, 'link':link, 'settings_link':settings_link,})
        message = template.render(context)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
    
    class Meta:
        ordering = ['-created_at']
    
class UpdateComment(models.Model):
    user = models.ForeignKey(User)
    update = models.ForeignKey(Update)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.update.title
        
    def get_absolute_url(self):
        return "/%s/projects/%i/updates/%i/#comment-%i" % (self.update.project.account, self.update.project.id, self.update.id, self.id)

    def send_update_comment(self, actor, verb, target, created_at, project, company, private_action):
        return action.send(sender=self, actor=actor, verb=verb, target=target, created_at=created_at, project=project, company=company, private_action=private_action)
    
class CanvasSet(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=100, blank=True)
    private_canvas = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User)    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def send_canvas_set(self, actor, verb, target, created_at, project, company, private_action):
        return action.send(sender=self, actor=actor, verb=verb, target=target, created_at=created_at, project=project, company=company, private_action=private_action)
        
    def num_of_versions(self):
        return Canvas.objects.filter(canvas_set=self).count()
        
    def get_absolute_url(self):
        return "/%s/projects/%i/canvases/%i/" % (self.project.account, self.project.id, self.id)
        
    def latest_canvas(self):
        #Gets the Most recent canvas version in this set.
        latest_canvases = Canvas.objects.filter(canvas_set=self).order_by('-version')[:1]
        for latest_canvas in latest_canvases:
            target_canvas = latest_canvas
        return target_canvas
    
    def get_latest_canvas_version_number(self):
        latest_canvases = Canvas.objects.filter(canvas_set=self).order_by('-version')[:1]
        for latest_canvas in latest_canvases:
            target_canvas = latest_canvas
        return target_canvas.version  

    def send_update_email(self, name, email, version):
        subject = u'Update to your business model canvas'
        link = 'http://%s/%s/projects/%i/canvases/%i/v/%i/' % (settings.SITE_HOST, self.project.account, self.project.id, self.id, version)
        settings_link = 'http://%s/%s/projects/%i/canvases/%i/' % (settings.SITE_HOST, self.project.account, self.project.id, self.id)
        template = get_template('projects/canvas_email.txt')
        context = Context({'name':name, 'canvas':self.name, 'link':link, 'settings_link':settings_link,})
        message = template.render(context)
        print "Called"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, email)
    
class Canvas(models.Model):
    project = models.ForeignKey(Project)
    canvas_set = models.ForeignKey(CanvasSet)
#    image = models.ImageField(null=True)
    notes = models.TextField(blank=True)
    canvas_type = models.CharField(max_length=1, choices=CANVAS_TYPE)
    version = models.IntegerField()
    tags = TagField()
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return "%s" % (self.canvas_set.name)
    
    def send_canvas(self, actor, verb, target, created_at, project, company, private_action):
        return action.send(sender=self, actor=actor, verb=verb, target=target, created_at=created_at, project=project, company=company, private_action=private_action)
        
    def get_absolute_url(self):
        return "/%s/projects/%i/canvases/%i/v/%i/" % (self.project.account, self.project.id, self.canvas_set.id, self.version)
    
    def has_more_versions(self):
        if Canvas.objects.filter(canvas_set=self.canvas_set).count() > 1:
            return True
            
    def add_canvas_url(self):
        return "/%s/projects/%i/canvases/%i/v/%i/new/" % (self.project.account, self.project.id, self.canvas_set.id, self.version)
        
    class Meta:
        verbose_name_plural = "Canvases"
        
    def send_comment_email(self, name, email):
        subject = u'New comment for your business model canvas'
        link = 'http://%s/%s/projects/%i/canvases/%i/v/%i/' % (settings.SITE_HOST, self.project.account, self.project.id, self.canvas_set.id, self.version)
        settings_link = 'http://%s/%s/projects/%i/canvases/%i/' % (settings.SITE_HOST, self.project.account, self.project.id, self.canvas_set.id)
        template = get_template('projects/canvas_comment_email.txt')
        context = Context({'name':name, 'canvas':self.canvas_set.name, 'link':link, 'settings_link':settings_link,})
        message = template.render(context)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])        
        
class NotificationList(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    target_object = generic.GenericForeignKey()
    account_user = models.ForeignKey(AccountUser)
    subscribed = models.BooleanField()
    
    def __str__(self):
        return "%s, %s" % (self.target_object, self.account_user.user)
    
class CanvasField(models.Model):
    canvas = models.ForeignKey(Canvas)
    block = models.CharField(max_length=2, blank=True, choices=CANVAS_BLOCK)
    order = models.IntegerField()
    colour = models.CharField(max_length=2, choices=CANVAS_COLOUR, default="YL")
    text = models.CharField(max_length=160)
    note = models.TextField()
    
    def get_name(self):
        names = {
            'cs':'Customer Segments',
            'cr':'Customer Relationships',
            'ch':'Channels',
            'vp':'Value Proposition',
            'ka':'Key Activities',
            'kr':'Key Resources',
            'kp':'Key Partners',
            'co':'Cost Structure',
            'rs':'Revenue Streams)',
        }
        return names[self.block]
        
    class Meta:
       ordering = ['order']

    
class CanvasComment(models.Model):
    canvas = models.ForeignKey(Canvas)
    user = models.ForeignKey(User)
    comment = models.TextField()
#    image = models.ImageField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def send_canvas_comment(self, actor, verb, target, created_at, project, company, private_action):
        return action.send(sender=self, actor=actor, verb=verb, target=target, created_at=created_at, project=project, company=company, private_action=private_action)
    
    def __str__(self):
        return self.canvas.canvas_set.name
        
    def get_absolute_url(self):
        return "/%s/projects/%i/canvases/%i/v/%i/#comment-%i" % (self.canvas.project.account, self.canvas.project.id, self.canvas.canvas_set.id, self.canvas.version, self.id)

class ActionManager(models.Manager):
    def stream_for_actor(self, actor):
        """
        Produces a QuerySet of most recent activities for any actor
        """
        return self.filter(
            actor = User.objects.filter(id=actor.pk),
        ).order_by('-created_at')

    def stream_for_model(self, model):
        """
        Produces a QuerySet of most recent activities for any model
        """
        return self.filter(
            content_type = ContentType.objects.get_for_model(model)
        ).order_by('-created_at')

class Action(models.Model):
    actor = models.ForeignKey(User)
    verb = models.CharField(max_length=100)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    target_object = generic.GenericForeignKey()
    project = models.ForeignKey(Project)
    #From what company did this action originate?
    company = models.ForeignKey(Company)
    private_action = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    objects = ActionManager()
    
    def actor_url(self):
        """
        Returns the URL to the ``actstream_actor`` view for the current actor
        """
        return reverse('actstream_actor', None,
            (self.user.id))
            
    def target_url(self):
        """
        Returns the URL to the ``actstream_actor`` view for the current target
        """        
        return reverse('actstream_actor', None,
            (self.content_type.pk, self.object_id))
    
    def timesince(self, now=None):
       """
       Shortcut for the ``django.utils.timesince.timesince`` function of the current timestamp
       """
       return timesince_(self.timestamp, now)
    
    class Meta:
       ordering = ['-created_at']
       
class Invitation(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    code = models.CharField(max_length=20)
    sender = models.ForeignKey(User)
    account = models.ForeignKey(Account)
    company = models.ForeignKey(Company)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return u'%s, %s' % (self.sender.username, self.email)
        
    def send(self):
        subject = u'Invitation to join BM Stack'
        link = 'http://%s/%s/invitation/%s/' % (settings.SITE_HOST, self.account.account, self.code)
        template = get_template('invitation/invitation_email.txt')
        context = Context({'name':self.name,'link':link,'sender':self.sender.get_full_name(),})
        message = template.render(context)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email])

def model_stream(model):
    return Action.objects.stream_for_model(model)
model_stream.__doc__ = Action.objects.stream_for_model.__doc__

def actor_stream(actor):
    return Action.objects.stream_for_actor(actor)
actor_stream.__doc__ = Action.objects.stream_for_actor.__doc__

def action_handler(verb, target=None, project=None, company=None, private_action=None, **kwargs):
    actor = kwargs.pop('actor')
    kwargs.pop('signal', None)
    action = Action(actor = actor,
                    verb = unicode(verb),
                    created_at=kwargs.pop('created_at', datetime.now()))
    if target:
        action.object_id = target.pk
        action.content_type = ContentType.objects.get_for_model(target)
    if project:
        action.project = project
    action.company = company
    action.private_action = private_action
    action.save()

def user_post_save(sender, instance, **kwargs):
    #Creates User Profile
    profile, new = UserProfile.objects.get_or_create(user=instance)
    
action.connect(action_handler, dispatch_uid="projects.models")
post_save.connect(user_post_save, sender=User)