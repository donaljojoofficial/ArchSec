from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Prefetch

from core.models import Project, ProjectAnalysis
from core.services.analysis_formatting import get_findings, get_quick_wins, get_roadmap, get_scorecards


def can_access_project(user, project):
    return user.is_staff or user.is_superuser or project.user_id == user.id


def can_access_analysis(user, analysis):
    return user.is_staff or user.is_superuser or analysis.user_id == user.id


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_project_list(request):
    projects = Project.objects.all().order_by("-created_at") if request.user.is_staff else Project.objects.filter(user=request.user).order_by("-created_at")
    return Response({
        "projects": [
            {
                "id": project.id,
                "name": project.name,
                "platform": project.platform,
                "tech_stack": project.tech_stack,
                "scale": project.scale,
                "budget": project.budget,
                "risk_level": project.risk_level,
                "created_at": project.created_at.isoformat(),
            }
            for project in projects
        ]
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_project_detail(request, project_id):
    try:
        project = Project.objects.prefetch_related(
            Prefetch("analyses", queryset=ProjectAnalysis.objects.order_by("-created_at"))
        ).get(id=project_id)
    except Project.DoesNotExist:
        return Response({"detail": "Not found."}, status=404)

    if not can_access_project(request.user, project):
        return Response({"detail": "Not found."}, status=404)

    return Response({
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "platform": project.platform,
        "tech_stack": project.tech_stack,
        "scale": project.scale,
        "budget": project.budget,
        "risk_level": project.risk_level,
        "structured_data": project.structured_data,
        "created_at": project.created_at.isoformat(),
        "analyses": [
            {
                "id": analysis.id,
                "created_at": analysis.created_at.isoformat(),
                "risk_category": analysis.risk_category,
                "modernization_score": analysis.security_score,
            }
            for analysis in project.analyses.all()
        ],
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_analysis_detail(request, analysis_id):
    try:
        analysis = ProjectAnalysis.objects.select_related("project").get(id=analysis_id)
    except ProjectAnalysis.DoesNotExist:
        return Response({"detail": "Not found."}, status=404)

    if not can_access_analysis(request.user, analysis):
        return Response({"detail": "Not found."}, status=404)

    return Response({
        "id": analysis.id,
        "project": {
            "id": analysis.project.id,
            "name": analysis.project.name,
        },
        "created_at": analysis.created_at.isoformat(),
        "risk_category": analysis.risk_category,
        "scores": get_scorecards(analysis),
        "executive_summary": analysis.executive_summary,
        "findings": get_findings(analysis),
        "quick_wins": get_quick_wins(analysis),
        "roadmap": get_roadmap(analysis),
        "diagrams": {
            "future_state": analysis.uml_diagram or "",
            "current_state": analysis.dfd_diagram or "",
            "ai_integration": analysis.erd_diagram or "",
            "deployment": analysis.threat_diagram or "",
            "security_testing": analysis.security_testing_diagram or "",
            "migration_roadmap": analysis.migration_roadmap_diagram or "",
        },
    })
