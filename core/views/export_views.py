from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from core.models.project_analysis import ProjectAnalysis
from core.models.project import Project
from core.services.auth_service import AuthorizationService
from core.decorators import analysis_owner_required, project_owner_required
import io
import zipfile
from django.utils.text import slugify
import logging

logger = logging.getLogger(__name__)


def build_export_content(analysis):
    return f"""
Modernization Assessment Report
===============================

System: {analysis.project.name}
Date: {analysis.created_at}
Modernization Priority Score: {analysis.security_score} ({analysis.risk_category})

Architecture Modernization
--------------------------
{analysis.architecture}

Security And Technical Debt Risks
---------------------------------
{analysis.threat_model}

Development And Deployment Modernization
----------------------------------------
{analysis.sdls_recommendations}

Cost, Effort, And Requirements
------------------------------
{analysis.cost_estimation}

Testing And Security Validation Plan
------------------------------------
{analysis.testing_plan}
""".strip()


@analysis_owner_required
def export_analysis_md(request, analysis_id):
    # Decorator already verified user has access to this analysis
    analysis = get_object_or_404(ProjectAnalysis, id=analysis_id)
    
    content = build_export_content(analysis)

    response = HttpResponse(content, content_type="text/markdown")
    response["Content-Disposition"] = f"attachment; filename=analysis_{analysis_id}.md"
    return response


@analysis_owner_required
def export_analysis_txt(request, analysis_id):
    # Decorator already verified user has access to this analysis
    analysis = get_object_or_404(ProjectAnalysis, id=analysis_id)
    
    content = build_export_content(analysis)

    response = HttpResponse(content, content_type="text/plain")
    response["Content-Disposition"] = f"attachment; filename=analysis_{analysis_id}.txt"
    return response

@project_owner_required
def export_analysis_history_zip(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    analyses = project.analyses.all().order_by("created_at")

    if not analyses.exists():
        messages.warning(request, "No analyses available to export.")
        return redirect('analysis_history', project_id=project_id)

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for analysis in analyses:
            filename = f"{slugify(project.name)}_{analysis.created_at.strftime('%Y-%m-%d_%H-%M')}.md"
            content = build_export_content(analysis)
            zip_file.writestr(filename, content)

    zip_buffer.seek(0)

    response = HttpResponse(zip_buffer, content_type="application/zip")
    response["Content-Disposition"] = (
        f"attachment; filename={slugify(project.name)}_analysis_history.zip"
    )
    return response
