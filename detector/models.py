from django.db import models
from django.contrib.auth.models import User

class ScanHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scans')
    filename = models.CharField(max_length=255, blank=True, null=True)
    analyzed_text = models.TextField()
    ai_probability = models.FloatField()
    perplexity = models.FloatField()
    burstiness = models.FloatField()
    heatmap_data = models.JSONField()  # Store list of dicts: {'text': string, 'color': string}
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['-created_at']
