import logging

from celery.result import AsyncResult
from celery.exceptions import CeleryError
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from kombu.exceptions import OperationalError

from core.decorators import analysis_owner_required, project_owner_required
from core.models.project import Project
from core.models.project_analysis import ProjectAnalysis
from core.services.analysis_formatting import get_findings, get_quick_wins, get_roadmap, get_scorecards
from core.tasks import generate_analysis_task

logger = logging.getLogger(__name__)


def run_analysis_without_broker(analysis):
    result = generate_analysis_task.apply(args=(analysis.id,), throw=False)
    if result.failed():
        if isinstance(result.result, Exception):
            raise result.result
        raise RuntimeError(str(result.result))


def build_assessment_comparison(analyses):
    completed = [analysis for analysis in analyses if analysis.risk_category not in ("Pending", "Error")]
    if len(completed) < 2:
        return None

    latest = completed[0]
    previous = completed[1]
    latest_findings = get_findings(latest)
    previous_findings = get_findings(previous)
    latest_titles = {finding["title"] for finding in latest_findings}
    previous_titles = {finding["title"] for finding in previous_findings}
    score_delta = latest.security_score - previous.security_score

    return {
        "latest": latest,
        "previous": previous,
        "score_delta": score_delta,
        "direction": "higher" if score_delta > 0 else "lower" if score_delta < 0 else "unchanged",
        "new_findings": sorted(latest_titles - previous_titles),
        "resolved_findings": sorted(previous_titles - latest_titles),
        "latest_count": len(latest_findings),
        "previous_count": len(previous_findings),
    }


@project_owner_required
def generate_analysis(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    analysis = ProjectAnalysis.objects.create(
        project=project,
        user=request.user,
        risk_category="Pending",
        security_score=0,
    )

    try:
        task = generate_analysis_task.delay(analysis.id)
        analysis.task_id = task.id
        analysis.save()
        messages.success(
            request,
            "Modernization assessment has been queued. You will be notified when it is complete.",
        )
    except (OperationalError, CeleryError, OSError, ConnectionError) as e:
        logger.warning("Redis/Celery connection failed: %s", e)
        if settings.DEBUG or getattr(settings, "ANALYSIS_SYNC_FALLBACK", False):
            try:
                run_analysis_without_broker(analysis)
                messages.success(
                    request,
                    "Modernization assessment completed locally because the background queue is unavailable.",
                )
                return redirect("dashboard")
            except Exception as fallback_error:
                logger.exception("Local analysis fallback failed: %s", fallback_error)

        analysis.risk_category = "Error"
        analysis.raw_ai_response = {
            "message": "Assessment queue is unavailable. Start Redis/Celery or enable local analysis fallback."
        }
        analysis.save()
        messages.error(request, "Assessment service is currently unavailable. Please try again later.")
    except Exception as e:
        logger.exception("Unexpected assessment queue failure: %s", e)
        analysis.risk_category = "Error"
        analysis.raw_ai_response = {"message": f"Assessment could not be queued: {e}"}
        analysis.save()
        messages.error(request, "Assessment could not be queued. Please try again later.")

    return redirect("dashboard")


@analysis_owner_required
def view_analysis(request, analysis_id):
    analysis = get_object_or_404(ProjectAnalysis.objects.select_related("project"), id=analysis_id)
    return render(request, "core/view_analysis.html", {
        "analysis": analysis,
        "project": analysis.project,
        "findings": get_findings(analysis),
        "quick_wins": get_quick_wins(analysis),
        "roadmap": get_roadmap(analysis),
        "scorecards": get_scorecards(analysis),
    })


@project_owner_required
def history_analysis(request, project_id):
    project = get_object_or_404(Project, id=project_id)
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
        "trend": trend_data,
        "comparison": build_assessment_comparison(list(analyses)),
    })


@analysis_owner_required
def analysis_status(request, analysis_id):
    analysis = get_object_or_404(ProjectAnalysis.objects.only("id", "task_id", "risk_category", "raw_ai_response"), id=analysis_id)
    task_status = "UNKNOWN"
    if analysis.task_id:
        try:
            task = AsyncResult(analysis.task_id)
            task_status = task.status
        except (OperationalError, CeleryError, OSError, ConnectionError) as exc:
            logger.warning("Unable to read Celery status for analysis %s: %s", analysis.id, exc)
            task_status = "UNAVAILABLE"

    payload = {
        "task_status": task_status,
        "assessment_status": analysis.risk_category,
        "analysis_id": analysis.id,
        "is_complete": analysis.risk_category not in ("Pending", "Error"),
        "is_error": analysis.risk_category == "Error",
    }
    if analysis.risk_category == "Error":
        raw_response = analysis.raw_ai_response if isinstance(analysis.raw_ai_response, dict) else {}
        payload["message"] = raw_response.get("message", "Assessment failed.")

    return JsonResponse(payload)


@analysis_owner_required
def download_analysis_pdf(request, analysis_id):
    analysis = get_object_or_404(ProjectAnalysis.objects.select_related("project"), id=analysis_id)
    project = analysis.project

    html = render_to_string("core/analysis_pdf.html", {
        "analysis": analysis,
        "project": project,
        "findings": get_findings(analysis),
        "quick_wins": get_quick_wins(analysis),
        "roadmap": get_roadmap(analysis),
        "scorecards": get_scorecards(analysis),
    })

    try:
        from weasyprint import HTML
    except (ImportError, OSError) as exc:
        logger.exception("WeasyPrint native dependency is unavailable: %s", exc)
        return HttpResponse(
            "PDF export is unavailable because WeasyPrint's native libraries are not installed.",
            status=503,
        )

    pdf_file = HTML(string=html).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="assessment_{analysis_id}.pdf"'

    return response
