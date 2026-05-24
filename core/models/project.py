from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    PLATFORM_CHOICES = [
        ('web', 'Web Application'),
        ('mobile', 'Mobile App'),
        ('api', 'API Service'),
        ('iot', 'IoT System'),
        ('cloud', 'Cloud Infrastructure'),
        ('other', 'Other'),
    ]

    RISK_LEVEL_CHOICES = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    description = models.TextField()
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    tech_stack = models.CharField(max_length=255)
    scale = models.CharField(max_length=255)
    budget = models.PositiveIntegerField(null=True, blank=True)
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # New structured data fields
    structured_data = models.JSONField(default=dict, blank=True)
    system_design_data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name
