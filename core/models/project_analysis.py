from django.db import models
from django.contrib.auth.models import User
from .project import Project


class ProjectAnalysis(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="analyses")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    architecture = models.TextField(blank=True)
    threat_model = models.TextField(blank=True)
    cost_estimation = models.TextField(blank=True)
    sdls_recommendations = models.TextField(blank=True)
    testing_plan = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    executive_summary = models.TextField(blank=True)

    security_score = models.IntegerField(default=0)
    risk_category = models.CharField(max_length=20, default="Unknown")

    critical_risks = models.TextField(blank=True)
    immediate_actions = models.TextField(blank=True)



    def __str__(self):
        return f"Analysis for {self.project.name} ({self.created_at})"


