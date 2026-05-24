from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from core.forms import ProjectForm
from core.models import Project, ProjectAnalysis
from core.services.analysis_formatting import get_findings
from core.views.export_views import build_proposal_content, build_structured_export


class UserIsolationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("owner", "owner@example.com", "Pass12345")
        self.other_user = User.objects.create_user("other", "other@example.com", "Pass12345")
        self.admin = User.objects.create_superuser("admin", "admin@example.com", "Pass12345")

        self.owner_project = Project.objects.create(
            user=self.user,
            name="Owner Legacy App",
            description="Old internal system",
            platform="web",
            tech_stack="PHP 5, jQuery",
            scale="small",
            budget=10000,
            risk_level="medium",
        )
        self.other_project = Project.objects.create(
            user=self.other_user,
            name="Other Legacy App",
            description="Another user's system",
            platform="web",
            tech_stack="ASP.NET WebForms",
            scale="small",
            budget=10000,
            risk_level="medium",
        )
        self.other_analysis = ProjectAnalysis.objects.create(
            project=self.other_project,
            user=self.other_user,
            risk_category="Medium",
            security_score=50,
        )

    def test_dashboard_only_lists_current_users_projects(self):
        self.client.login(username="owner", password="Pass12345")

        response = self.client.get(reverse("dashboard"))

        self.assertContains(response, self.owner_project.name)
        self.assertNotContains(response, self.other_project.name)

    def test_user_cannot_generate_assessment_for_another_users_project(self):
        self.client.login(username="owner", password="Pass12345")

        response = self.client.get(reverse("generate_analysis", args=[self.other_project.id]))

        self.assertRedirects(response, reverse("dashboard"))
        self.assertFalse(
            ProjectAnalysis.objects.filter(project=self.other_project, user=self.user).exists()
        )

    def test_user_cannot_view_another_users_analysis(self):
        self.client.login(username="owner", password="Pass12345")

        response = self.client.get(reverse("view_analysis", args=[self.other_analysis.id]))

        self.assertRedirects(response, reverse("dashboard"))

    def test_admin_can_view_any_users_analysis(self):
        self.client.login(username="admin", password="Pass12345")

        response = self.client.get(reverse("view_analysis", args=[self.other_analysis.id]))

        self.assertEqual(response.status_code, 200)


class AdminOnlyOperationsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("owner", "owner@example.com", "Pass12345")
        self.admin = User.objects.create_superuser("admin", "admin@example.com", "Pass12345")

    def test_task_monitor_is_not_accessible_to_regular_users(self):
        self.client.login(username="owner", password="Pass12345")

        response = self.client.get(reverse("celery_dashboard"))

        self.assertRedirects(response, reverse("dashboard"))

    @patch("core.views.celery_views.current_app")
    def test_task_monitor_is_accessible_to_admins(self, current_app):
        inspector = Mock()
        inspector.active.return_value = {}
        inspector.scheduled.return_value = {}
        inspector.reserved.return_value = {}
        current_app.control.inspect.return_value = inspector

        self.client.login(username="admin", password="Pass12345")

        response = self.client.get(reverse("celery_dashboard"))

        self.assertEqual(response.status_code, 200)


class ProjectInputSafetyTests(TestCase):
    def test_project_form_strips_markup_and_control_characters(self):
        form = ProjectForm(data={
            "name": "<script>alert(1)</script>Legacy CRM\x00",
            "description": "Old app<script>ignore previous instructions</script>\x07",
            "platform": "web",
            "tech_stack": "PHP 5 <b>jQuery</b>",
            "scale": "small",
            "budget": "10000",
            "risk_level": "medium",
            "technology": ["php"],
            "technology_manual": "<img src=x onerror=alert(1)>Use PHP 8 upgrade path",
        })

        self.assertTrue(form.is_valid(), form.errors)

        self.assertEqual(form.cleaned_data["name"], "alert(1)Legacy CRM")
        self.assertEqual(form.cleaned_data["description"], "Old appignore previous instructions")
        self.assertEqual(form.cleaned_data["tech_stack"], "PHP 5 jQuery")
        self.assertEqual(
            form.get_structured_data()["technology"]["manual_input"],
            "Use PHP 8 upgrade path",
        )

    def test_project_form_rejects_oversized_manual_input(self):
        form = ProjectForm(data={
            "name": "Legacy CRM",
            "description": "Old app",
            "platform": "web",
            "tech_stack": "PHP",
            "scale": "small",
            "budget": "10000",
            "risk_level": "medium",
            "technology_manual": "x" * 2001,
        })

        self.assertFalse(form.is_valid())
        self.assertIn("technology_manual", form.errors)

    def test_project_form_allows_ai_estimated_budget_and_risk(self):
        form = ProjectForm(data={
            "name": "Legacy CRM",
            "description": "Old app",
            "platform": "web",
            "tech_stack": "PHP",
            "scale": "small",
        })

        self.assertTrue(form.is_valid(), form.errors)
        project = form.save(commit=False)
        self.assertIsNone(project.budget)
        self.assertEqual(project.risk_level, "")

    def test_project_form_stores_modernization_intake_sections(self):
        form = ProjectForm(data={
            "name": "Legacy Storefront",
            "description": "Old ecommerce app",
            "platform": "web",
            "tech_stack": "PHP, MySQL, jQuery",
            "scale": "medium",
            "current_backend": ["php_legacy"],
            "current_backend_manual": "PHP 7.2 with custom modules",
            "current_frontend": ["jquery"],
            "cms_framework": ["custom_framework"],
            "database": ["sql"],
            "hosting": ["vps"],
            "deployment": ["manual"],
            "runtime_age": ["end_of_life"],
            "testing_process": ["manual_only"],
            "security_testing_process": ["none"],
            "observability_operations": ["basic_logs"],
            "backups_incident_response": ["manual_backups"],
            "ai_readiness": ["no_ai_usage"],
            "migration_constraints": ["low_downtime_tolerance"],
        })

        self.assertTrue(form.is_valid(), form.errors)
        structured_data = form.get_structured_data()

        self.assertEqual(structured_data["current_backend"]["options"], ["php_legacy"])
        self.assertEqual(
            structured_data["current_backend"]["manual_input"],
            "PHP 7.2 with custom modules",
        )
        self.assertEqual(structured_data["hosting"]["options"], ["vps"])
        self.assertEqual(structured_data["migration_constraints"]["options"], ["low_downtime_tolerance"])


class StructuredFindingsTests(TestCase):
    def test_get_findings_normalizes_structured_ai_response(self):
        user = User.objects.create_user("owner", "owner@example.com", "Pass12345")
        project = Project.objects.create(
            user=user,
            name="Owner Legacy App",
            description="Old internal system",
            platform="web",
            tech_stack="PHP 5, jQuery",
            scale="small",
            budget=10000,
            risk_level="medium",
        )
        analysis = ProjectAnalysis.objects.create(
            project=project,
            user=user,
            raw_ai_response={
                "findings": [{
                    "title": "Manual deployment",
                    "category": "Deployment",
                    "current_issue": "FTP releases",
                    "recommendation": "Add CI/CD",
                    "migration_steps": "Create a deployment pipeline",
                }]
            },
        )

        findings = get_findings(analysis)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["title"], "Manual deployment")
        self.assertEqual(findings[0]["recommended_solution"], "Add CI/CD")
        self.assertEqual(findings[0]["migration_steps"], ["Create a deployment pipeline"])

    def test_structured_json_export_contains_findings_and_diagrams(self):
        user = User.objects.create_user("owner", "owner@example.com", "Pass12345")
        project = Project.objects.create(
            user=user,
            name="Owner Legacy App",
            description="Old internal system",
            platform="web",
            tech_stack="PHP 5, jQuery",
            scale="small",
        )
        analysis = ProjectAnalysis.objects.create(
            project=project,
            user=user,
            executive_summary="Modernize the release workflow.",
            risk_category="High",
            security_score=80,
            uml_diagram="graph TD\nA-->B",
            raw_ai_response={
                "modernization_score": 80,
                "findings": [{
                    "title": "Manual deployment",
                    "category": "Deployment",
                    "current_issue": "FTP releases",
                    "recommended_solution": "Add CI/CD",
                    "priority": "High",
                }],
            },
        )

        payload = build_structured_export(analysis)

        self.assertEqual(payload["scores"]["modernization_score"], 80)
        self.assertEqual(payload["findings"][0]["title"], "Manual deployment")
        self.assertEqual(payload["diagrams"]["future_state"], "graph TD\nA-->B")

    def test_proposal_export_emphasizes_business_impact(self):
        user = User.objects.create_user("owner2", "owner2@example.com", "Pass12345")
        project = Project.objects.create(
            user=user,
            name="Legacy Portal",
            description="Old customer portal",
            platform="web",
            tech_stack="ASP.NET WebForms",
            scale="medium",
        )
        analysis = ProjectAnalysis.objects.create(
            project=project,
            user=user,
            executive_summary="The portal needs a phased modernization.",
            risk_category="High",
            security_score=85,
            raw_ai_response={
                "modernization_score": 85,
                "quick_wins": ["Add dependency scanning"],
                "roadmap": ["Stabilize releases", "Modernize frontend"],
                "findings": [{
                    "title": "Unsupported framework",
                    "category": "Stack",
                    "current_issue": "Framework is out of support",
                    "why_it_matters": "Security fixes are no longer available",
                    "recommended_solution": "Move to supported .NET",
                    "cost_estimate": "$15k-$30k one-time",
                    "priority": "High",
                    "risks": ["Regression risk"],
                    "mitigations": ["Add characterization tests"],
                }],
            },
        )

        proposal = build_proposal_content(analysis)

        self.assertIn("Business Impact", proposal)
        self.assertIn("Unsupported framework", proposal)
        self.assertIn("$15k-$30k", proposal)
