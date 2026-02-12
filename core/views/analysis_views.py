import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from celery.result import AsyncResult
from django.template.loader import render_to_string
from weasyprint import HTML
from celery import current_app
from django.contrib.admin.views.decorators import staff_member_required
from kombu.exceptions import OperationalError

from core.models.project import Project
from core.models.project_analysis import ProjectAnalysis
from core.services.ai_client import generate_ai_analysis
from core.services.security_scoring import calculate_final_security_score
from core.tasks import generate_analysis_task

logger = logging.getLogger(__name__)


@login_required
def generate_analysis(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)

    # Create an initial analysis object to show "Pending" status
    analysis = ProjectAnalysis.objects.create(
        project=project,
        user=request.user,
        risk_category="Pending",
        security_score=0,
    )

    try:
        # Start the asynchronous analysis task
        task = generate_analysis_task.delay(analysis.id)

        # Store the task ID in the analysis object to track its status
        analysis.task_id = task.id
        analysis.save()

        messages.success(request, "✅ Analysis has been queued. You will be notified when it is complete.")
    except OperationalError as e:
        logger.warning(f"Redis/Celery connection failed: {e}")
        analysis.risk_category = "Error"
        analysis.save()
        messages.error(request, "❌ Analysis service is currently unavailable. Please try again later.")

    return redirect("dashboard")


@login_required
def view_analysis(request, analysis_id):
    analysis = get_object_or_404(ProjectAnalysis, id=analysis_id, user=request.user)
    return render(request, "core/view_analysis.html", {
        "analysis": analysis,
        "project": analysis.project
    })


@login_required
def history_analysis(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    analyses = ProjectAnalysis.objects.filter(project=project).order_by("-created_at")

    scores = [a.security_score for a in analyses if a.security_score > 0]

    trend_data = {
        "highest": max(scores) if scores else 0,
        "lowest": min(scores) if scores else 0,
        "average": sum(scores) / len(scores) if scores else 0,
        "improving": scores[-1] < scores[0] if len(scores) > 1 else False,
    }

    return render(request, "core/analysis_history.html", {
        "project": project,
        "analyses": analyses,
        "trend": trend_data
    })


@login_required
def analysis_status(request, analysis_id):
    analysis = get_object_or_404(ProjectAnalysis, id=analysis_id, user=request.user)
    task = AsyncResult(analysis.task_id)
    return JsonResponse({"status": task.status})

@login_required
def download_analysis_pdf(request, analysis_id):
    analysis = get_object_or_404(ProjectAnalysis, id=analysis_id, user=request.user)
    project = analysis.project

    html = render_to_string("core/analysis_pdf.html", {
        "analysis": analysis,
        "project": project
    })

    pdf_file = HTML(string=html).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="analysis_{analysis_id}.pdf"'

    return response
