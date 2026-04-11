from django.db import models
from django.contrib.auth.models import User

class ResumeAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    resume_file = models.FileField(upload_to='resumes/')
    job_description = models.TextField()
    ats_score = models.CharField(max_length=50, blank=True, null=True) # Low, Medium, High
    gap_analysis = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"Analysis for {username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
