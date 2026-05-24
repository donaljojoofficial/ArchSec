# Generated manually for explicit modernization diagram support.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0016_make_budget_and_risk_optional"),
    ]

    operations = [
        migrations.AddField(
            model_name="projectanalysis",
            name="security_testing_diagram",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="projectanalysis",
            name="migration_roadmap_diagram",
            field=models.TextField(blank=True, null=True),
        ),
    ]
