# urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core.views import register_view, dashboard
from core.views.project_views import create_project
from core.views.analysis_views import generate_analysis, view_analysis, history_analysis, download_analysis_pdf, analysis_status
from core.views.export_views import export_analysis_md, export_analysis_txt
from core.views.export_views import export_analysis_history_zip
from core.views.notification_views import notification_list, mark_notification_as_read, clear_all_notifications

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('register/', register_view, name='register'),

    # Project actions
    path("project/create/", create_project, name="create_project"),
    path("project/<int:project_id>/analysis/", generate_analysis, name="generate_analysis"),
    path("analysis/<int:analysis_id>/", view_analysis, name="view_analysis"),
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
    path("project/<int:project_id>/analysis/history/export/",export_analysis_history_zip,name="export_analysis_history_zip"),


    # Dashboard last (so it doesn't override other routes)
    path("dashboard/", dashboard, name="dashboard"),
    path("", dashboard, name="home"),
]
