from django.contrib import admin
from django.urls import path, include
from core.views.dashboard_views import dashboard
from core.views.project_views import create_project
from core.views.analysis_views import generate_analysis, view_analysis, history_analysis, download_analysis_pdf
from core.views.export_views import export_analysis_md, export_analysis_txt
from core.views.export_views import export_analysis_history_zip

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),

    # Project actions
    path("project/create/", create_project, name="create_project"),
    path("project/<int:project_id>/analysis/", generate_analysis, name="generate_analysis"),
    path("analysis/<int:analysis_id>/", view_analysis, name="view_analysis"),
    path("project/<int:project_id>/analysis/history/", history_analysis, name="analysis_history"),
    path("analysis/<int:analysis_id>/pdf/", download_analysis_pdf, name="download_analysis_pdf"),
    # Export actions
    path("analysis/<int:analysis_id>/export/md/", export_analysis_md, name="export_analysis_md"),
    path("analysis/<int:analysis_id>/export/txt/", export_analysis_txt, name="export_analysis_txt"),
    path("project/<int:project_id>/analysis/history/export/",export_analysis_history_zip,name="export_analysis_history_zip"),


    # Dashboard last (so it doesn't override other routes)
    path("", dashboard, name="dashboard"),
]



