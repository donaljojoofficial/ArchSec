from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from core.models.project_analysis import ProjectAnalysis
from core.models.project import Project
from core.decorators import analysis_owner_required, project_owner_required
from core.services.analysis_formatting import get_findings, get_quick_wins, get_roadmap, get_scorecards
import io
import zipfile
from django.utils.text import slugify
import logging

logger = logging.getLogger(__name__)


def render_list(items):
    return "\n".join(f"- {item}" for item in items) if items else "- Not specified"


def build_findings_export(analysis):
    findings = get_findings(analysis)
    if not findings:
        return ""

    sections = ["Modernization Findings", "----------------------"]
    for index, finding in enumerate(findings, start=1):
        sections.extend([
            "",
            f"{index}. {finding['title']}",
            "~" * (len(f"{index}. {finding['title']}")),
            f"Category: {finding['category']}",
            f"Priority: {finding['priority']}",
            "",
            f"Current issue: {finding['current_issue']}",
            f"Why it matters: {finding['why_it_matters']}",
            f"Recommended solution: {finding['recommended_solution']}",
            f"Cost estimate: {finding['cost_estimate'] or 'Not estimated'}",
            f"Effort: {finding['effort'] or 'Not specified'}",
            "",
            "Tools and services:",
            render_list(finding["tools_services"]),
            "",
            "Required skills:",
            render_list(finding["required_skills"]),
            "",
            "Migration steps:",
            render_list(finding["migration_steps"]),
            "",
            "Dependencies:",
            render_list(finding["dependencies"]),
            "",
            "Risks:",
            render_list(finding["risks"]),
            "",
            "Mitigations:",
            render_list(finding["mitigations"]),
            "",
            "Expected benefits:",
            render_list(finding["expected_benefits"]),
        ])
    return "\n".join(sections)


def build_export_content(analysis):
    scorecards = get_scorecards(analysis)
    findings_export = build_findings_export(analysis)
    quick_wins = get_quick_wins(analysis)
    roadmap = get_roadmap(analysis)

    if findings_export:
        return f"""
Modernization Assessment Report
===============================

System: {analysis.project.name}
Date: {analysis.created_at}
Modernization Priority Score: {scorecards['modernization_score']} ({analysis.risk_category})
AI Readiness Score: {scorecards['ai_readiness_score'] if scorecards['ai_readiness_score'] is not None else 'Not scored'}
Technical Debt Score: {scorecards['technical_debt_score'] if scorecards['technical_debt_score'] is not None else 'Not scored'}
Security Risk Score: {scorecards['security_risk_score'] if scorecards['security_risk_score'] is not None else 'Not scored'}
Migration Risk Score: {scorecards['migration_risk_score'] if scorecards['migration_risk_score'] is not None else 'Not scored'}

Executive Summary
-----------------
{analysis.executive_summary}

{findings_export}

Quick Wins
----------
{render_list(quick_wins)}

Roadmap
-------
{render_list(roadmap)}
""".strip()


def build_proposal_content(analysis):
    scorecards = get_scorecards(analysis)
    findings = get_findings(analysis)
    quick_wins = get_quick_wins(analysis)
    roadmap = get_roadmap(analysis)

    if not findings:
        return build_export_content(analysis)

    high_priority = [
        finding for finding in findings
        if finding["priority"].lower() in ("critical", "high")
    ]

    proposal_sections = [
        "Modernization Proposal",
        "======================",
        "",
        f"Client/System: {analysis.project.name}",
        f"Assessment Date: {analysis.created_at}",
        f"Modernization Priority Score: {scorecards['modernization_score']} ({analysis.risk_category})",
        "",
        "Executive Summary",
        "-----------------",
        analysis.executive_summary or "No executive summary was generated.",
        "",
        "Business Impact",
        "---------------",
    ]

    if high_priority:
        for finding in high_priority:
            proposal_sections.append(f"- {finding['title']}: {finding['why_it_matters']}")
    else:
        proposal_sections.append("- No critical or high-priority findings were generated.")

    proposal_sections.extend([
        "",
        "Recommended Scope",
        "-----------------",
    ])
    for finding in findings:
        proposal_sections.extend([
            f"- {finding['title']} ({finding['priority']}): {finding['recommended_solution']}",
            f"  Estimated cost/effort: {finding['cost_estimate'] or finding['effort'] or 'To be estimated during planning'}",
        ])

    proposal_sections.extend([
        "",
        "Quick Wins",
        "----------",
        render_list(quick_wins),
        "",
        "Delivery Roadmap",
        "----------------",
        render_list(roadmap),
        "",
        "Key Risks And Mitigations",
        "-------------------------",
    ])

    for finding in findings:
        if finding["risks"] or finding["mitigations"]:
            proposal_sections.append(f"{finding['title']}:")
            proposal_sections.append(render_list(finding["risks"]))
            proposal_sections.append("Mitigations:")
            proposal_sections.append(render_list(finding["mitigations"]))

    proposal_sections.extend([
        "",
        "Assumptions",
        "-----------",
        "- Costs are planning estimates and should be validated against vendor pricing, team capacity, and production constraints.",
        "- Migration work should be phased to protect current operations and reduce downtime risk.",
        "- Security and compliance checks should be included before each production release.",
    ])

    return "\n".join(proposal_sections).strip()


def build_structured_export(analysis):
    scorecards = get_scorecards(analysis)
    return {
        "id": analysis.id,
        "system": analysis.project.name,
        "created_at": analysis.created_at.isoformat(),
        "risk_category": analysis.risk_category,
        "scores": scorecards,
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
        "raw_ai_response": analysis.raw_ai_response,
    }

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


@analysis_owner_required
def export_analysis_json(request, analysis_id):
    analysis = get_object_or_404(ProjectAnalysis, id=analysis_id)
    content = build_structured_export(analysis)

    response = JsonResponse(content, json_dumps_params={"indent": 2})
    response["Content-Disposition"] = f"attachment; filename=analysis_{analysis_id}.json"
    return response


@analysis_owner_required
def export_analysis_proposal(request, analysis_id):
    analysis = get_object_or_404(ProjectAnalysis, id=analysis_id)
    content = build_proposal_content(analysis)

    response = HttpResponse(content, content_type="text/markdown")
    response["Content-Disposition"] = f"attachment; filename=proposal_{analysis_id}.md"
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
