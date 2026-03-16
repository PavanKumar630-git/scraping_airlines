
from django.db import models

class LufhansaDocument(models.Model):
    
    pdf_url = models.URLField()
    file_path = models.CharField(max_length=500)
    source = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
