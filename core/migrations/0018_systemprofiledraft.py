from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0017_modernization_diagram_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="SystemProfileDraft",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source", models.CharField(choices=[("document", "Document upload"), ("chat", "Chat collector")], max_length=20)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("ready", "Ready for review"), ("converted", "Converted to project")], default="draft", max_length=20)),
                ("uploaded_file", models.FileField(blank=True, null=True, upload_to="intake_documents/%Y/%m/")),
                ("original_filename", models.CharField(blank=True, max_length=255)),
                ("extracted_text", models.TextField(blank=True)),
                ("collected_data", models.JSONField(blank=True, default=dict)),
                ("missing_fields", models.JSONField(blank=True, default=list)),
                ("confidence", models.JSONField(blank=True, default=dict)),
                ("chat_history", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("project", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="intake_drafts", to="core.project")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="system_profile_drafts", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
