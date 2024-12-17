from django.contrib import admin
from django.contrib.auth.models import Group

from ks_account.models import User, ActivityLog
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as origGroupAdmin


class AccountUserAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'username', 'is_active', 'mobile', 'mobile_active_code']

    class Meta:
        model = User

    # def get_groups(self, user):
    #     return "\n".join([g for g in user.groups.all()])


class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user', 'type', 'description', 'create_date']

    class Meta:
        model = ActivityLog







class GroupAdminForm(forms.ModelForm):
    """
    ModelForm that adds an additional multiple select field for managing
    the users in the group.
    """
    users = forms.ModelMultipleChoiceField(
        User.objects.all(),
        widget=admin.widgets.FilteredSelectMultiple('Users', False),
        required=False,
        )


    def __init__(self, *args, **kwargs):
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            initial_users = self.instance.user_set.values_list('pk', flat=True)
            self.initial['users'] = initial_users


    def save(self, *args, **kwargs):
        kwargs['commit'] = True
        return super(GroupAdminForm, self).save(*args, **kwargs)


    def save_m2m(self):
        self.instance.user_set.clear()
        self.instance.user_set.add(*self.cleaned_data['users'])


class GroupAdmin(origGroupAdmin):
    """
    Customized GroupAdmin class that uses the customized form to allow
    management of users within a group.
    """
    form = GroupAdminForm

admin.site.unregister(Group)
# Register the modified GroupAdmin with the admin site
# admin_site = admin.AdminSite(name='my_admin')
admin.site.register(Group, GroupAdmin)

admin.site.register(User, AccountUserAdmin)
admin.site.register(ActivityLog, ActivityLogAdmin)