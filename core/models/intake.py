from django.contrib.auth.models import User
from django.db import models


class SystemProfileDraft(models.Model):
    SOURCE_CHOICES = [
        ("document", "Document upload"),
        ("chat", "Chat collector"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("ready", "Ready for review"),
        ("converted", "Converted to project"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="system_profile_drafts")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    uploaded_file = models.FileField(upload_to="intake_documents/%Y/%m/", blank=True, null=True)
    original_filename = models.CharField(max_length=255, blank=True)
    extracted_text = models.TextField(blank=True)
    collected_data = models.JSONField(default=dict, blank=True)
    missing_fields = models.JSONField(default=list, blank=True)
    confidence = models.JSONField(default=dict, blank=True)
    chat_history = models.JSONField(default=list, blank=True)
    project = models.ForeignKey(
        "core.Project",
        on_delete=models.SET_NULL,
        related_name="intake_drafts",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_source_display()} draft for {self.user}"
