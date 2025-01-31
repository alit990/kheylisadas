from django.contrib import admin

from ks_tag.models import Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active']

    class Meta:
        model = Tag


admin.site.register(Tag, TagAdmin)
