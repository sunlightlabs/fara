from django.db import models
from django.contrib import admin

class Document(models.Model):
    url = models.URLField()
    reg_id = models.IntegerField(max_length=5)
    doc_type = models.CharField(max_length=100, null=True)
    stamp_date = models.DateField(null=True, blank=True) 
    #add some file storage or links to lobby tracker?
    
    def __unicode__(self):
        return "%s---  Date: %s" %(self.url, self.stamp_date)
admin.site.register(Document)