from django.db import models
from django.contrib import admin

class Proposed(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=200)
    location_id = models.IntegerField(null=True, blank=True)
    # from DSCAmodels.IntegerField(
    dsca_url = models.URLField(null=True, blank=True)
    pdf_url = models.URLField(null=True, blank=True)
    print_url = models.URLField(null=True, blank=True)
    
    def __unicode__(self):
        return "%s, %s" %(self.title, self.date)

class proposed_admin(admin.ModelAdmin):
    search_fields=['title']
admin.site.register(Proposed, proposed_admin)

