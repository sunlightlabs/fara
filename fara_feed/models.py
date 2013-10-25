from django.db import models
from django.contrib import admin

class Document(models.Model):
    url = models.URLField(db_index=True)
    reg_id = models.IntegerField(max_length=5)
    doc_type = models.CharField(max_length=100, null=True)
    stamp_date = models.DateField(null=True, blank=True) 
    processed = models.BooleanField(default=False)
    #add some file storage or links to lobby tracker?
    
    def __unicode__(self):
        return "%s ---%s---  Date: %s" %(self.reg_id, self.url, self.stamp_date)
