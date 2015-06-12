from django.contrib import admin
from core.models import Pasty, Source

class PastyAdmin(admin.ModelAdmin):
    list_display = ('date', 'source', 'get_html', 'votes', )
    list_filter = ('date', 'source', )
    search_fields = ('text', )
    date_hierarchy = 'date'
    fields = ('date', 'source', 'text', 'votes')

    def get_html(self, obj):
        return obj.html()
    get_html.allow_tags = True

admin.site.register(Pasty, PastyAdmin)

class SourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'sync_url', 'sync_date',)
admin.site.register(Source, SourceAdmin)

