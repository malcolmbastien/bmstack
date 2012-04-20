from django import forms
from django.forms import ModelForm
from projects.models import AccountUser, Account, Company, Project
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

class AddAccountForm(forms.Form):
    site_address = forms.SlugField(max_length=60)
    company = forms.CharField(max_length=100)
        
class AccountForm(forms.Form):
    #billing info
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=75)
    company = forms.CharField(max_length=100)
    
    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput)    
    site_address = forms.CharField(max_length=60)
    
    def clean_username(self):
        #make sure the user name is unique
        data = self.cleaned_data['username']
        try:
            User.objects.get(username=data)
            raise forms.ValidationError("Username already taken.")
        except ObjectDoesNotExist:
            return data
        
    def clean_site_address(self):
        #make sure the site_address is unique
        data = self.cleaned_data['site_address']
        try:
            Account.objects.get(account=data)
            raise forms.ValidationError("Site address already taken.")
        except ObjectDoesNotExist:
            return data

#probably should delete this
class PersonForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=75)
    
class ProjectForm(forms.Form):
    name = forms.CharField(max_length=60)
    
    def __init__(self, account, user, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        account_user = AccountUser.objects.get(account=account, user=user)
        # Get all companies from this account, but filters out the user's own company.
        self.fields['companies'] = forms.MultipleChoiceField(required=False, choices=[ (o.id, str(o)) for o in Company.objects.filter(account=account).exclude(id=account_user.company.id)])
    
class ProjectEditForm(forms.Form):
#    name = forms.CharField(max_length=60)
#    note = forms.CharField(widget=forms.Textarea)
#    status = forms.CharField(max_length=60)
    
    def __init__(self, project, account, user, *args, **kwargs):
        super(ProjectEditForm, self).__init__(*args, **kwargs)
        account_user = AccountUser.objects.get(account=account, user=user)
        # Get all companies from this account, but filters out the user's own company.
        self.fields['name'] = forms.CharField(max_length=60, initial=project.name)
        self.fields['note'] = forms.CharField(widget=forms.Textarea, initial=project.note, required=False)
        self.fields['status'] = forms.CharField(max_length=60, initial=project.status, required=False)
        self.fields['companies'] = forms.MultipleChoiceField(required=False, choices=[ (o.id, str(o)) for o in Company.objects.filter(account=account).exclude(id=account_user.company.id)])
        
class AddCanvasForm(forms.Form):
    canvas = forms.CharField(widget=forms.HiddenInput, required=False)
    label = forms.CharField(max_length=100)
    notes = forms.CharField(widget=forms.Textarea)
    tags = forms.CharField(max_length=400)

    class Media:
        js = ('js/add_canvas_form.js',)
        
class NewCanvasForm(forms.Form):
    canvas = forms.CharField(widget=forms.HiddenInput, required=False)
    label = forms.CharField(max_length=100)
    notes = forms.CharField(widget=forms.Textarea)
    tags = forms.CharField(max_length=400)
    private_canvas = forms.BooleanField(required=False)
    
    class Media:
        js = ('js/new_canvas_form.js',)

class CompanyForm(forms.Form):
    name = forms.CharField(max_length=100)
    
class CanvasFieldForm(forms.Form):
    CANVAS_COLOUR = (
        ('BK', 'Black'),
        ('BL', 'Blue'),
        ('RD', 'Red')
    )
    block = forms.CharField(widget=forms.HiddenInput, required=False)
    text = forms.CharField(max_length=160)
    
class CanvasCommentForm(forms.Form):
    #Later this will have some stuff to do with replying with your own canvas or image.
    comment = forms.CharField(widget=forms.Textarea)

class UpdateForm(forms.Form):
    title = forms.CharField(max_length=140)
    update = forms.CharField(widget=forms.Textarea)
    private_update = forms.BooleanField(required=False)
    
class UpdateCommentForm(forms.Form):
    #Later this will have some stuff to do with replying with your own canvas or image.
    comment = forms.CharField(widget=forms.Textarea)
    
class AccountUserForm(forms.Form):
    def __init__(self, account, *args, **kwargs):
        super(AccountUserForm, self).__init__(*args, **kwargs)
        # Get all companies from this account.
        self.fields['company'] = forms.ChoiceField(required=True, choices=[(o.id, str(o)) for o in Company.objects.filter(account=account)])

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)

class SettingsForm(ModelForm):
    class Meta:
        model = Account
        fields = ('site_name',)

class InviteForm(forms.Form):
    name = forms.CharField(label=u'Name')
    email = forms.EmailField(label=u'Email')
    
class InviteJoinForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput, max_length=30)
