from django.db import models
from django.contrib.auth.models import User
from .project import Project


class ProjectAnalysis(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="analyses")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    raw_ai_response = models.JSONField(null=True, blank=True)
    task_id = models.CharField(max_length=255, blank=True, null=True)

    architecture = models.TextField(blank=True)
    threat_model = models.TextField(blank=True)
    cost_estimation = models.TextField(blank=True)
    sdls_recommendations = models.TextField(blank=True)
    testing_plan = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    security_score = models.IntegerField(default=0)
    risk_category = models.CharField(max_length=20, default="Unknown")

    critical_risks = models.TextField(blank=True)
    executive_summary = models.TextField(blank=True)
    top_risks = models.TextField(blank=True)
    immediate_actions = models.TextField(blank=True, null=True)
    likelihood = models.IntegerField(default=0)   # 1–5
    impact = models.IntegerField(default=0)       # 1–5
