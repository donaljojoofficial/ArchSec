# Generated manually for the modernization intake update.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0015_userprofile"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="budget",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="project",
            name="risk_level",
            field=models.CharField(
                blank=True,
                choices=[
                    ("low", "Low Risk"),
                    ("medium", "Medium Risk"),
                    ("high", "High Risk"),
                ],
                max_length=20,
            ),
        ),
    ]
