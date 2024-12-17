from django.contrib import admin

from ks_site.models import ContactUs, FrequentQuestion, FrequentQuestionCategory, AgeCategory, SiteSetting, Avatar, \
    Reference, AccountSetting

# Register your models here.
admin.site.register(Reference)
admin.site.register(Avatar)
admin.site.register(SiteSetting)
admin.site.register(AccountSetting)
admin.site.register(ContactUs)
admin.site.register(FrequentQuestionCategory)
admin.site.register(FrequentQuestion)
admin.site.register(AgeCategory)
