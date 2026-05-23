from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from core.models import Project, ProjectAnalysis


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
