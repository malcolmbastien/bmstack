from projects.models import Project, Update, UpdateComment, CanvasSet, Canvas, NotificationList, CanvasField, CanvasComment, Action, Company, Account, AccountUser, UserProfile, Invitation
from django.contrib import admin

admin.site.register(Project)
admin.site.register(Update)
admin.site.register(UpdateComment)
admin.site.register(CanvasSet)
admin.site.register(Canvas)
admin.site.register(NotificationList)
admin.site.register(CanvasField)
admin.site.register(CanvasComment)
admin.site.register(Action)
admin.site.register(Company)
admin.site.register(Account)
admin.site.register(AccountUser)
admin.site.register(UserProfile)
admin.site.register(Invitation)