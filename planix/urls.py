# urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core.views import register_view, logout_view, profile_view, edit_profile_view, change_password_view, dashboard, celery_dashboard, health_check, view_diagrams, landing_page, about_page, help_page
from core.views.project_views import create_project
from core.views.analysis_views import generate_analysis, view_analysis, history_analysis, download_analysis_pdf, analysis_status
from core.views.export_views import export_analysis_json, export_analysis_md, export_analysis_proposal, export_analysis_txt
from core.views.export_views import export_analysis_history_zip
from core.views.notification_views import notification_list, mark_notification_as_read, clear_all_notifications
from core.views.api_views import api_analysis_detail, api_project_detail, api_project_list

from core.logging_config import configure_logging

# Initialize structured logging
configure_logging()

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', edit_profile_view, name='edit_profile'),
    path('profile/change-password/', change_password_view, name='change_password'),

    # Project actions
    path("project/create/", create_project, name="create_project"),
    path("project/<int:project_id>/analysis/", generate_analysis, name="generate_analysis"),
    path("analysis/<int:analysis_id>/", view_analysis, name="view_analysis"),
    path("analysis/<int:analysis_id>/diagrams/", view_diagrams, name="view_diagrams"),
    path("project/<int:project_id>/analysis/history/", history_analysis, name="analysis_history"),
    path("analysis/<int:analysis_id>/pdf/", download_analysis_pdf, name="download_analysis_pdf"),
    path("analysis/<int:analysis_id>/status/", analysis_status, name="analysis_status"),
    
    # Notification actions
    path("notifications/", notification_list, name="notifications"),
    path("notifications/<int:notification_id>/read/", mark_notification_as_read, name="mark_notification_as_read"),
    path("notifications/clear/", clear_all_notifications, name="clear_all_notifications"),

    # Export actions
    path("analysis/<int:analysis_id>/export/md/", export_analysis_md, name="export_analysis_md"),
    path("analysis/<int:analysis_id>/export/txt/", export_analysis_txt, name="export_analysis_txt"),
    path("analysis/<int:analysis_id>/export/json/", export_analysis_json, name="export_analysis_json"),
    path("analysis/<int:analysis_id>/export/proposal/", export_analysis_proposal, name="export_analysis_proposal"),
    path("project/<int:project_id>/analysis/history/export/",export_analysis_history_zip,name="export_analysis_history_zip"),

    # API
    path("api/projects/", api_project_list, name="api_project_list"),
    path("api/projects/<int:project_id>/", api_project_detail, name="api_project_detail"),
    path("api/analyses/<int:analysis_id>/", api_analysis_detail, name="api_analysis_detail"),

    path("celery-dashboard/", celery_dashboard, name="celery_dashboard"),
    path("health/", health_check, name="health_check"),
    path("about/", about_page, name="about"),
    path("help/", help_page, name="help"),

    # Dashboard last (so it doesn't override other routes)
    path("dashboard/", dashboard, name="dashboard"),
    path("", landing_page, name="home"),
]
