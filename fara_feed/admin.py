from django.contrib import admin

from fara_feed.models import Document

class doc_admin(admin.ModelAdmin):
    search_fields=['reg_id', 'stamp_date', 'url' ]

admin.site.register(Document, doc_admin)