from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list_detail import object_list, object_detail
from django.template import RequestContext
from projects.models import *
from forms import *
from projects.models import actor_stream, model_stream
from datetime import datetime
from collections import defaultdict
from tagging.models import Tag, TaggedItem
import smtplib

@login_required
def index(request, account):
    account = get_object_or_404(Account, account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    
    #Gets the list of projects the user has access to.
    projects = Project.objects.filter(companies=account_user.company)

    #only actions from projects that the user has access to.
    #from the projects you *do* have access to, hide the actions that are private (private updates, comments on those updates, etc...)
    #actions = Action.objects.filter(project__companies=account_user.company).filter(private_action=False).filter(private_action=True,company=account_user.company).order_by('-project', '-created_at')
    
    actions = Action.objects.filter(project__companies=account_user.company)
    actions1 = actions.filter(private_action=False)
    actions2 = actions.filter(private_action=True,company=account_user.company)
    actions = actions1 | actions2
    
    return render_to_response('projects/index.html', {'account': account, 'actions': actions, 'projects':projects},
                                context_instance=RequestContext(request))

@login_required 
def project_detail(request, account, project_id):
    account = get_object_or_404(Account, account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    project = get_object_or_404(Project, pk=project_id)

    #actions = Action.objects.filter(project=project_id).filter(private_action=False).filter(private_action=True,company=account_user.company)
    actions = Action.objects.filter(project=project_id)
    actions1 = actions.filter(private_action=False)
    actions2 = actions.filter(private_action=True,company=account_user.company)
    actions = actions1 | actions2
    
    paginator = Paginator(actions,20)
    try:
        page = int(request.GET.get('page','1'))
    except ValueError:
        page = 1
        
    try:
        action_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        action_list = paginator.page(paginator.num_pages)
    
    return render_to_response('projects/project_detail.html', {'project':project, 'account':account, 'action_list':action_list}, context_instance=RequestContext(request))

@login_required    
def project_list(request, account):
    account = get_object_or_404(Account, account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    project_list = Project.objects.filter(account__account=account).order_by('name')

    return render_to_response('projects/project_list.html', {'project_list':project_list, 'account':account}, context_instance=RequestContext(request))

@login_required
def canvas_set_list(request, account, project_id):
    account = get_object_or_404(Account, account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    canvas_set_list = CanvasSet.objects.filter(project__id=project_id).order_by('-id')
    project = get_object_or_404(Project, pk=project_id)
    
    paginator = Paginator(canvas_set_list, 5)

    try:
        page = int(request.GET.get('page','1'))
    except ValueError:
        page = 1

    try:
        canvas_sets = paginator.page(page)
    except (EmptyPage, InvalidPage):
        canvas_sets = paginator.page(paginator.num_pages)

    return render_to_response('projects/canvas_set_list.html', {'canvas_sets':canvas_sets, 'account':account, 'project':project}, context_instance=RequestContext(request))

@login_required
def with_tag(request, account, project_id, tag, objects_id=None):
    project = get_object_or_404(Project, pk=project_id)
    account = get_object_or_404(Account, account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    query_tag = Tag.objects.get(name=tag)
    
    canvas_list = TaggedItem.objects.get_by_model(Canvas, query_tag)
    canvas_list = canvas_list.order_by('-created_at')
    
    paginator = Paginator(canvas_list, 10)
    
    try:
        page = int(request.GET.get('page','1'))
    except ValueError:
        page = 1
    
    try:
        canvases = paginator.page(page)
    except (EmptyPage, InvalidPage):
        canvases = paginator.page(paginator.num_pages)
        
    return render_to_response('projects/with_tag.html', {'account':account, 'project':project, 'query_tag':query_tag, 'canvases':canvases}, context_instance=RequestContext(request))
    
@login_required
def canvas_list(request, account, project_id):
    canvas_list = Canvas.objects.filter(project__id=project_id).order_by('-id')
    project = get_object_or_404(Project, pk=project_id)
    account = get_object_or_404(Account, account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    
    paginator = Paginator(canvas_list, 10)
    
    try:
        page = int(request.GET.get('page','1'))
    except ValueError:
        page = 1
    
    try:
        canvases = paginator.page(page)
    except (EmptyPage, InvalidPage):
        canvases = paginator.page(paginator.num_pages)
        
    return render_to_response('projects/canvas_list.html', {'canvases':canvases, 'account':account, 'project':project}, context_instance=RequestContext(request))

@login_required
def canvas_set_detail(request, account, project_id, canvas_set_id):
    canvas_set = get_object_or_404(CanvasSet, pk=canvas_set_id)
    project = get_object_or_404(Project, pk=project_id)
    canvas_list = Canvas.objects.filter(canvas_set=canvas_set.id).order_by('-created_at')
    account = get_object_or_404(Account, account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    account_user = AccountUser.objects.get(user=request.user)
    ctype = ContentType.objects.get_for_model(canvas_set)
    notification_list = NotificationList.objects.filter(content_type__pk=ctype.id, object_id=canvas_set.id)
    
    try:
        notify_this_user = NotificationList.objects.get(content_type__pk=ctype.id, object_id=canvas_set.id, account_user=account_user)
        notify_this_user = notify_this_user.subscribed
    except ObjectDoesNotExist:
        notify_this_user = False
    
    paginator = Paginator(canvas_list, 5)
    
    try:
        page = int(request.GET.get('page','1'))
    except ValueError:
        page = 1
    
    try:
        canvases = paginator.page(page)
    except (EmptyPage, InvalidPage):
        canvases = paginator.page(paginator.num_pages)
        
    return render_to_response('projects/canvas_set_detail.html', {'canvases':canvases, 'notify_this_user':notify_this_user, 'notification_list':notification_list, 'canvas_set':canvas_set, 'project':project, 'account':account}, context_instance=RequestContext(request))

@login_required
def subscribe_canvas_updates(request, account, project_id, canvas_set_id):
    user = request.user
    account = Account.objects.get(account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    project = Project.objects.get(pk=project_id)
    canvas_set = CanvasSet.objects.get(pk=canvas_set_id)
    account_user = AccountUser.objects.get(user=user)
    ctype=ContentType.objects.get_for_model(canvas_set)

    try:
        notify = NotificationList.objects.get(content_type__pk=ctype.id, object_id=canvas_set.id, account_user=account_user)
        if notify.subscribed == False:
            notify.subscribed = True
        else:
            notify.subscribed = False
        notify.save()
    except ObjectDoesNotExist:
        notify = NotificationList(content_type=ctype, object_id=canvas_set.id, account_user=account_user,subscribed=True)
        notify.save()

    return HttpResponseRedirect(reverse('canvas_set_detail', kwargs={'account':account.account, 'project_id':project.id, 'canvas_set_id':canvas_set.id}))

@login_required
def subscribe_update_updates(request, account, project_id, update_id):
    user = request.user
    account = Account.objects.get(account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    project = Project.objects.get(pk=project_id)
    update = Update.objects.get(pk=update_id)
    ctype = ContentType.objects.get_for_model(update)
    account_user = AccountUser.objects.get(user=user)
    
    try:
        notify = NotificationList.objects.get(content_type__pk=ctype.id, object_id=update.id, account_user=account_user)
        if notify.subscribed == False:
            notify.subscribed = True
        else:
            notify.subscribed = False
        notify.save()
    except ObjectDoesNotExist:
        notify = NotificationList(content_type=ctype, object_id=update.id, account_user=account_user, subscribed=True)
        notify.save()

    return HttpResponseRedirect(reverse('update_detail', kwargs={'account':account.account, 'project_id':project.id, 'update_id':update.id}))

@login_required
def canvas_detail(request, account, project_id, canvas_set_id, canvas_version):
    project = get_object_or_404(Project, pk=project_id)
    canvas_set = get_object_or_404(CanvasSet, pk=canvas_set_id)
    canvas = get_object_or_404(Canvas, canvas_set=canvas_set, version=canvas_version)
    canvas_comments = CanvasComment.objects.filter(canvas=canvas.id).order_by('created_at')
    account = get_object_or_404(Account, account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    user = request.user

    canvas_fields = defaultdict(list)
    fields = CanvasField.objects.filter(canvas=canvas.id)
    for field in fields:
        canvas_fields[field.block].append(field)
                
    if request.method == 'POST':
        form = CanvasCommentForm(request.POST)
        if form.is_valid():
            cc = CanvasComment()
            cc.canvas = canvas
            cc.user = request.user
            cc.comment = form.cleaned_data['comment']
            cc.save()
            
            if canvas_set.private_canvas == True:
                private_action = True
            else:
                private_action = False
                
            company = account_user.company
                
            cc.send_canvas_comment(cc.user, "posted by", cc, cc.created_at, project, company, private_action)
            update_canvas_comment_subscribers(canvas, account_user)
            return HttpResponseRedirect('/%s/projects/%d/canvases/%d/v/%d' % (account, int(project_id), canvas_set.id, canvas.version))
    else:
        form = CanvasCommentForm()
    return render_to_response('projects/canvas_detail.html', {'canvas':canvas, 'user':user, 'account':account,'canvas_fields':canvas_fields,'canvas_comments':canvas_comments,'project':project,'form':form}, context_instance=RequestContext(request))
    
@login_required
def update_list(request, account, project_id):
    project = get_object_or_404(Project, pk=project_id)
    account = get_object_or_404(Account, account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    update_list = Update.objects.filter(project__id=project_id)
    paginator = Paginator(update_list, 10)
    
    try:
        page = int(request.GET.get('page','1'))
    except ValueError:
        page = 1
    
    try:
        updates = paginator.page(page)
    except (EmptyPage, InvalidPage):
        updates = paginator.page(paginator.num_pages)
    return render_to_response('projects/update_list.html', {'updates':updates, 'project':project, 'account':account}, context_instance=RequestContext(request))

@login_required
def update_detail(request, account, project_id, update_id):
    update = get_object_or_404(Update, pk=update_id)
    project = get_object_or_404(Project, pk=project_id)
    account = get_object_or_404(Account, account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    update_comments = UpdateComment.objects.filter(update=update_id).order_by('created_at')
    ctype = ContentType.objects.get_for_model(update)
    notification_list = NotificationList.objects.filter(content_type__pk=ctype.id, object_id=update.id)
    
    try:
         notify_this_user = NotificationList.objects.get(content_type__pk=ctype.id, object_id=update.id, account_user=account_user)
         notify_this_user = notify_this_user.subscribed
    except ObjectDoesNotExist:
         notify_this_user = False
    
    if request.method == 'POST':
        form = UpdateCommentForm(request.POST)
        if form.is_valid():
            uc = UpdateComment()
            uc.update = Update.objects.get(id=update_id)
            uc.user = request.user
            uc.comment = form.cleaned_data['comment']
            uc.save()
            
            company = account_user.company
            if update.private_update == True:
                private_action = True
            else:
                private_action = False
                
            update_subscribers(update,uc, account_user)
            uc.send_update_comment(uc.user, "posted by", uc, uc.created_at, uc.update.project, company, private_action)
            return HttpResponseRedirect('/%s/projects/%d/updates/%d/' % (account, int(project_id), int(update_id)))
    else:
        form = CanvasCommentForm()
    return render_to_response('projects/update_detail.html', {'update':update, 'notify_this_user':notify_this_user, 'notification_list':notification_list, 'account':account, 'project':project, 'form': form, 'update_comments':update_comments}, context_instance=RequestContext(request))

@login_required
def company_list(request, account):
    account = get_object_or_404(Account, account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    queryset = []
    company_list = Company.objects.filter(account__account=account)
    for company in company_list:
        employee_list = []
        employees = AccountUser.objects.filter(company=company).order_by('id')
        for employee in employees:
            employee_list.append(employee)
        queryset.append([company, employee_list])
    return render_to_response('projects/company_list.html', {'company_list':queryset,'account': account}, context_instance=RequestContext(request))
    
@login_required
def people_detail(request, account, user_id):
    queryset = AccountUser.objects.all()
    object_id = user_id
    account = get_object_or_404(Account, account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    return object_detail(request, queryset=queryset, object_id=object_id,
                        extra_context={'account': account})

@login_required
def edit_profile(request, account, user_id):
    account = Account.objects.get(account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    account_user = AccountUser.objects.get(user=user_id)
    if request.method == 'POST':
        form = AccountUserForm(account, request.POST, prefix='account_user')
        user_form = UserForm(request.POST, instance=request.user, prefix='user')
        if form.is_valid() and user_form.is_valid():
            account_user.company = get_object_or_404(Company, pk=form.cleaned_data['company'])
            account_user.save()
            user_form.save()
            return HttpResponseRedirect('/%s/companies/' % account)
    else:
        form = AccountUserForm(account, prefix='account_user')
        user_form = UserForm(instance=request.user, prefix='user')
    return render_to_response('projects/edit_profile.html', {'user_form':user_form, 'account':account, 'form':form}, context_instance=RequestContext(request))

@login_required
def delete_project(request, account, project_id):
    account = Account.objects.get(account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    project = get_object_or_404(Project, pk=project_id)
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.is_prime_company():
        project_name = project.name
        project.delete()
        request.user.message_set.create(message='The project "%s" was deleted.' % project_name)
    return HttpResponseRedirect('/')


@login_required
def edit_project(request, account, project_id):
    account = Account.objects.get(account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    project = Project.objects.get(pk=project_id)
    
    if request.method == 'POST':
        form = ProjectEditForm(project, account, request.user, request.POST)
        if form.is_valid():
            project.name = form.cleaned_data['name']
            project.note = form.cleaned_data['note']
            project.status = form.cleaned_data['status']
            project.companies.clear()
            
            project.companies.add(account_user.company)
            
            companies = form.cleaned_data['companies']
            for company in companies:
                company = Company.objects.get(id=company)
                project.companies.add(company)
            project.save()
            return HttpResponseRedirect('/%s/projects/%i/' % (account, project.id))
    else:
        form = ProjectEditForm(project, account, request.user)
    return render_to_response('projects/edit_project.html', {'account':account,'project':project,'form':form}, context_instance=RequestContext(request))
    
@login_required
def settings(request, account):
    account = Account.objects.get(account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    
    if request.method == 'POST':
        form = SettingsForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/%s/' % account)
    else:
        form = SettingsForm(instance=account)
    return render_to_response('projects/account_settings.html', {'account':account, 'form':form}, context_instance=RequestContext(request))
    
@login_required
def account(request, account):
    account = Account.objects.get(account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    return render_to_response('projects/account_upgrade.html', {'account':account}, context_instance=RequestContext(request))
    
@login_required
def user_profile_settings(request):
    user = request.user
    return render_to_response('projects/settings.html', {'user':user}, context_instance=RequestContext(request))
        
def save_new_canvas(request):
    #Saves a new canvas with a new Canvas Set.
    data = request.POST.iteritems()
    account_name = request.POST.get("account")
    project_id = request.POST.get("project_id")
    name = request.POST.get("label")
    private_canvas = request.POST.get("private_canvas")
    if private_canvas == "on":
        private_canvas = True
    else:
        private_canvas = False
    notes = request.POST.get("notes")
    tags = request.POST.get("tags")

    project = get_object_or_404(Project, pk=project_id)
    account = get_object_or_404(Account, account=account_name)
    account_user = get_object_or_404(AccountUser, user=request.user, account=account)
    
    blocks = ['kp','ka','kr','vp','cr','ch','cs','co','rs']  
    
    cs = CanvasSet()
    cs.name = name
    cs.project = Project.objects.get(id=project_id)
    cs.created_by = request.user
    cs.private_canvas = private_canvas
    cs.save()

    c = Canvas()
    c.project = Project.objects.get(id=project_id)
    c.canvas_set = cs
    c.notes = notes
    c.created_by = request.user
    c.version = 1
    c.save()
    
    Tag.objects.update_tags(c, tags)
    
    #Save new canvas field objects
    for block in blocks:
        item_position = 0
        while request.POST.get("canvas_data[" + block + "][" + str(item_position) + "][id]") != None:
            cf = CanvasField()
            cf.canvas = c
            cf.block = block
            cf.text = request.POST.get("canvas_data["+block+"]["+str(item_position)+"][text]")
            cf.colour = request.POST.get("canvas_data["+block+"]["+str(item_position)+"][colour]")
            cf.note = request.POST.get("canvas_data["+block+"]["+str(item_position)+"][note]")
            cf.order = item_position
            cf.save()
            
            item_position = item_position + 1
    
    ctype=ContentType.objects.get_for_model(cs)
    notify = NotificationList(content_type=ctype, object_id=cs.id, account_user=account_user,subscribed=True)
    notify.save()
    
    company = account_user.company
    if cs.private_canvas == True:
        private_action = True
    else:
        private_action = False
    
    c.send_canvas(c.created_by, "created by", c, c.created_at, c.project, company, private_action)
    target_url = '/%s/projects/%d/canvases/%d/v/%d/' % (account, c.project.id, cs.id, c.version)
    return HttpResponse(target_url)

@login_required
def canvas_new(request, account, project_id):
    CanvasFieldFormSet = formset_factory(CanvasFieldForm, extra=9, max_num=9)
    project = get_object_or_404(Project, id=project_id)
    account = get_object_or_404(Account, account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    blocks = ['kp','ka','kr','vp','cr','ch','cs','co','rs']  
    field_forms = {}                           
        
    if request.method == 'POST':
        form = NewCanvasForm(request.POST, request.FILES, prefix='canvas')
        if form.is_valid():
                    cs = CanvasSet()
                    cs.name = form.cleaned_data['label']
                    cs.project = Project.objects.get(id=project_id)
                    cs.created_by = request.user
                    cs.save()
                                        
                    c = Canvas()
                    c.project = Project.objects.get(id=project_id)
                    c.canvas_set = cs
                    c.created_by = request.user
                    c.version = 0
                    c.save()
                    
                    company = account_user.company
                    if cs.private_canvas == True:
                        private_action = True
                    else:
                        private_action = False
                    
                    c.send_canvas(cs.created_by, "created by", c, c.created_at, c.project, company, private_action)
                    return HttpResponseRedirect('/%s/projects/%d/canvases/%d/' % (account, c.project.id, c.id))

    else:
        form = NewCanvasForm(prefix='canvas')        
        for block in blocks:
            field_forms[block] = CanvasFieldForm(initial={'block':block}, prefix=block)
    return render_to_response('projects/new_canvas.html', {'field_forms':field_forms, 'form':form, 'account':account, 'project':project}, context_instance=RequestContext(request))

def save_add_canvas(request):
    #Saves a new canvas in an existing Canvas set
    data = request.POST.iteritems()
    account_name = request.POST.get("account")
    project_id = request.POST.get("project_id")
    name = request.POST.get("label")
    notes = request.POST.get("notes")
    canvas_set_id = request.POST.get("canvas_set_id")
    canvas_id = request.POST.get("canvas_id")
    tags = request.POST.get("tags")
    #Action = either "new" or "update"
    action = request.POST.get("action")
        
    account_user = get_object_or_404(AccountUser, user=request.user)
    project = get_object_or_404(Project, id=project_id)
    account = get_object_or_404(Account, account=account_name)

    blocks = ['kp','ka','kr','vp','cr','ch','cs','co','rs']  

    cs = CanvasSet.objects.get(id=canvas_set_id)

    if action == "new":
        c = Canvas()
        c.project = Project.objects.get(id=project.id)
        c.canvas_set = cs
        c.created_by = request.user
        c.version = cs.get_latest_canvas_version_number() + 1
        
    if action == "update":
        c = get_object_or_404(Canvas, id=canvas_id)
        CanvasField.objects.filter(canvas=c).delete()
    
    c.notes = notes
    c.save()

    Tag.objects.update_tags(c, tags)
    
    #Save new canvas field objects
    for block in blocks:
        item_position = 0
        while request.POST.get("canvas_data[" + block + "][" + str(item_position) + "][id]") != None:
            cf = CanvasField()
            cf.canvas = c
            cf.block = block
            cf.text = request.POST.get("canvas_data["+block+"]["+str(item_position)+"][text]")
            cf.colour = request.POST.get("canvas_data["+block+"]["+str(item_position)+"][colour]")
            cf.note = request.POST.get("canvas_data["+block+"]["+str(item_position)+"][note]")
            cf.order = item_position
            cf.save()
            item_position = item_position + 1


    company = account_user.company
    if cs.private_canvas == True:
        private_action = True
    else:
        private_action = False
        
    if action == "new":
        c.send_canvas(c.created_by, "created by", c, c.created_at, c.project, company, private_action)
    if action == "update":
        c.send_canvas(request.user, "updated by", c, c.created_at, c.project, company, private_action)

    ctype=ContentType.objects.get_for_model(cs)    
    try:
        nl = NotificationList.objects.get(content_type__pk=ctype.id, object_id=cs.id, account_user=account_user)
    except ObjectDoesNotExist:
        notify = NotificationList(content_type=ctype, object_id=cs.id, account_user=account_user,subscribed=True)
        notify.save()
    update_canvas_subscribers(cs, c.version, account_user)
    target_url = '/%s/projects/%d/canvases/%d/v/%d/' % (account, c.project.id, cs.id, c.version)
    return HttpResponse(target_url)


@login_required
def canvas_add(request, account, project_id, canvas_set_id, **kwargs):
    # Adds a new version of a canvas to an existing canvas set
    CanvasFieldFormSet = formset_factory(CanvasFieldForm, extra=9, max_num=9)
    project = get_object_or_404(Project, id=project_id)
    account = get_object_or_404(Account, account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    blocks = ['kp','ka','kr','vp','cr','ch','cs','co','rs']  
    field_forms = {}
    canvas_set = get_object_or_404(CanvasSet, pk=canvas_set_id)
    
    tags_str = ""
    if kwargs:
        canvas = Canvas.objects.get(canvas_set=canvas_set, version=kwargs["canvas_version"])
        tags = Tag.objects.get_for_object(canvas)
        for tag in tags:
            tags_str = tags_str + tag.name + ","
    
    if request.method == 'POST':
        form = AddCanvasForm(request.POST, request.FILES, prefix='canvas')
        if form.is_valid():
                    cs = CanvasSet()
                    cs.name = form.cleaned_data['label']
                    cs.project = Project.objects.get(id=project_id)
                    cs.created_by = request.user
                    cs.save()

                    c = Canvas()
                    c.project = Project.objects.get(id=project_id)
                    c.canvas_set = cs
                    c.created_by = request.user
                    c.version = 0
                    c.save()

                    company = account_user.company
                    if cs.private_canvas == True:
                        private_action = True
                    else:
                        private_action = False
                        
                    c.send_canvas(cs.created_by, "created by", c, c.created_at, c.project, company, private_action)
                    return HttpResponseRedirect('/%s/projects/%d/canvases/%d/' % (account, c.project.id, c.id))

    else:
        form = AddCanvasForm(prefix='canvas')
        if kwargs:
            data = serializers.serialize('json', CanvasField.objects.filter(canvas=canvas))
            form = AddCanvasForm(prefix='canvas', initial={'notes':canvas.notes, 'tags':tags_str})
        else:
            data = 0
            canvas = False
        
        for block in blocks:
            field_forms[block] = CanvasFieldForm(initial={'block':block}, prefix=block)
    return render_to_response('projects/add_canvas.html', {'field_forms':field_forms, 'form':form, 'data':data, 'account':account, 'project':project, 'canvas_set':canvas_set, 'canvas':canvas}, context_instance=RequestContext(request))

@login_required
def account_add(request):
    if request.method == 'POST':
        form = AddAccountForm(request.POST)
        if form.is_valid():
            a = Account()
            ac = AccountUser()
            c = Company()
            u = request.user
                        
            a.account = form.cleaned_data['site_address']
            a.site_name = form.cleaned_data['company']
            a.save()
            
            c.name = form.cleaned_data['company']
            c.account = a
            c.save()
            
            ac.account = a
            ac.user = u
            ac.company = c
            ac.save()
            
            return HttpResponseRedirect('/%s/' % a.account)
    else:
        form = AddAccountForm()
    return render_to_response('projects/add_account.html', {'form':form}, context_instance=RequestContext(request))

def account_new(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            a = Account()            
            c = Company()
            u = User()
            
            ac = AccountUser()

            a.account = form.cleaned_data['site_address']
            a.site_name = form.cleaned_data['company']
            a.save()

            c.name = form.cleaned_data['company']
            c.account = a
            c.prime = True
            c.save()
            
            username = form.cleaned_data['username'].lower()
            password = form.cleaned_data['password']
            u.username = username
            u.first_name = form.cleaned_data['first_name']
            u.last_name = form.cleaned_data['last_name']
            u.email = form.cleaned_data['email']
            u.set_password(password)
            u.save()
            
            ac.account = a
            ac.user = u
            ac.company = c
            ac.save()
            
            user = authenticate(username=u.username, password=password)
            if user is not None:
                if user.is_active:
                    login(request,user)
            return HttpResponseRedirect('/%s/' % a.account)
    else:
        form = AccountForm()
    return render_to_response('projects/signup.html', {'form':form}, context_instance=RequestContext(request))

@login_required
def project_new(request, account):
    account = get_object_or_404(Account, account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    if request.method == 'POST':
        form = ProjectForm(account, request.user, request.POST)
        if form.is_valid():
            p = Project()
            p.account = Account.objects.get(account=account)
            p.name = form.cleaned_data['name']
            p.user = request.user
            p.save()
            p.companies.add(account_user.company)
            companies = form.cleaned_data['companies']
            for company in companies:
                company = Company.objects.get(id=company)
                p.companies.add(company)
            p.save()
            
            company = account_user.company
            private_action = False
                
            p.send_project(p.user, "created by", p, p.created_at, p, company, private_action)
            return HttpResponseRedirect('/%s/projects/%d' % (account, p.id))
    else:
        form = ProjectForm(account, request.user)
    return render_to_response('projects/new_project.html', {'form':form, 'account':account}, context_instance=RequestContext(request))
    
@login_required
def update_new(request, account, project_id):
    account = get_object_or_404(Account, account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    if request.method == 'POST':
        form = UpdateForm(request.POST)
        if form.is_valid():
            u = Update()
            u.title = form.cleaned_data['title']
            u.update = form.cleaned_data['update']
            u.private_update = form.cleaned_data['private_update']
            u.project = Project.objects.get(id=project_id)
            u.user = request.user
            u.save()
            
            company = account_user.company
            if u.private_update == True:
                private_action = True
            else:
                private_action = False
                                
            ctype=ContentType.objects.get_for_model(u)
            try:
                nl = NotificationList.objects.get(content_type__pk=ctype.id, object_id=u.id, account_user=account_user)
            except ObjectDoesNotExist:
                notify = NotificationList(content_type=ctype, object_id=u.id, account_user=account_user,subscribed=True)
                notify.save()
                
            u.send_update(u.user, "posted by", u, u.created_at, u.project, company, private_action)
            return HttpResponseRedirect('/%s/projects/%d/updates/' % (account, int(project_id)))
    else:
        form = UpdateForm()
    return render_to_response('projects/new_update.html', {'form':form, 'account':account, 'project_id':project_id}, context_instance=RequestContext(request))
    
@login_required
def new_company(request, account):
    account = get_object_or_404(Account, account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            c = Company()
            c.name = form.cleaned_data['name']
            
            a = get_object_or_404(Account, account=account)
            c.account = a
            c.save()
            return HttpResponseRedirect('/%s/companies/' % account)
    else:
        form = CompanyForm()
    return render_to_response('projects/new_company.html', {'form':form, 'account':account}, context_instance=RequestContext(request))    
            
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')
    
def home(request):
    users = User.objects.count()
    projects = Project.objects.count()
    canvases = Canvas.objects.count()
    if request.user.is_authenticated():
        accountuser = AccountUser.objects.get(user=request.user)
        return HttpResponseRedirect('/%s' % accountuser.account.account)
    return render_to_response('home.html', {'users':users, 'projects':projects, 'canvases':canvases}, context_instance=RequestContext(request))

def update_subscribers(update, comment, account_user):
    ctype = ContentType.objects.get_for_model(update)
    notification_list = NotificationList.objects.filter(content_type__pk=ctype.id, object_id=update.id, subscribed=True)
    
    for notify in notification_list:
        if (notify.account_user != account_user):
            name = notify.account_user.user.first_name
            email = notify.account_user.user.email
            try:
                update.send_update_email(name,email,comment)
            except:
                pass
    
def update_canvas_subscribers(canvas_set, version, account_user):
    """
    Called whenever a canvas is updated, and whenever a new version of a canvas
    is added to a canvas_set this function sends an email out to subscribers
    """
    ctype = ContentType.objects.get_for_model(canvas_set)
    notification_list = NotificationList.objects.filter(content_type__pk=ctype.id, object_id=canvas_set.id, subscribed=True)
    
    for notify in notification_list:
        if (notify.account_user != account_user):
            name = notify.account_user.user.first_name
            email = notify.account_user.user.email
            try:
                canvas_set.send_update_email(name,email,version)
            except:
                pass
        
def update_canvas_comment_subscribers(canvas, account_user):
    ctype = ContentType.objects.get_for_model(canvas.canvas_set)
    notification_list = NotificationList.objects.filter(content_type__pk=ctype.id, object_id=canvas.canvas_set.id, subscribed=True)
    
    for notify in notification_list:
        if (notify.account_user != account_user):
            name = notify.account_user.user.first_name
            email = notify.account_user.user.email
            try:
                canvas.send_comment_email(name, email)
            except:
                pass
    
@login_required
def invite(request, account, company_id):
    account = get_object_or_404(Account, account=account)
    account_user = get_object_or_404(AccountUser, account=account, user=request.user)
    if request.method == 'POST':
        form = InviteForm(request.POST)
        if form.is_valid():
            invitation = Invitation(name=form.cleaned_data['name'],
                                        email=form.cleaned_data['email'],
                                        code=User.objects.make_random_password(20),
                                        account=Account.objects.get(account=account),
                                        company=Company.objects.get(id=company_id),
                                        sender=request.user
                                    )
            invitation.save()
            try:
                invitation.send()
                request.user.message_set.create(message=u'An invitation was sent to %s.' % invitation.email)
            except smtplib.SMTPException:
                request.user.message_set.create(message=u'An error occured when sending the invitation.')
            return HttpResponseRedirect('/%s/companies/' % account)
    else:
        form = InviteForm()
    return render_to_response('invitation/invite.html', {'form':form, 'account':account,'company_id':company_id}, context_instance=RequestContext(request))
            
def invite_accept(request, account, code):
    invitation = get_object_or_404(Invitation, code__exact=code)
    request.session['invitation'] = invitation.id
    return HttpResponseRedirect('/%s/new_user/' % account)
    
def invite_join(request, account):
    if 'invitation' in request.session:
        invitation = Invitation.objects.get(id=request.session['invitation'])
        account = Account.objects.get(account=invitation.account)
        company = Company.objects.get(id=invitation.company.id)
        if request.method == 'POST':
            form = InviteJoinForm(request.POST)
            if form.is_valid():
                u = User()
                u.username = form.cleaned_data['username'].lower()
                u.first_name = form.cleaned_data['first_name']
                u.last_name = form.cleaned_data['last_name']
                u.email = invitation.email
                u.set_password(form.cleaned_data['password'])
                u.save()
                
                ac = AccountUser()
                ac.account = account
                ac.user = u
                ac.company = invitation.company
                ac.save()
                
                invitation.delete()
                del request.session['invitation']
                return HttpResponseRedirect('/%s/' % account.account)
        else:
            form = InviteJoinForm()
        return render_to_response('invitation/invite_join.html', {'form':form, 'account':account,'company':company}, context_instance=RequestContext(request))
