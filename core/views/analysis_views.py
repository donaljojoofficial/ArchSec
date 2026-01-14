import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

from core.models.project import Project
from core.models.project_analysis import ProjectAnalysis
from core.services.ai_client import generate_ai_analysis
from core.services.security_scoring import calculate_final_security_score


@login_required
def generate_analysis(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)

    structured_data_str = ""
    if project.structured_data:
        for section, data in project.structured_data.items():
            structured_data_str += f"## {section.upper().replace('_', ' ')}\n"
            if data.get('options'):
                structured_data_str += "Selected Options:\n"
                for option in data['options']:
                    structured_data_str += f"- {option}\n"
            if data.get('manual_input'):
                structured_data_str += "Manual Input:\n"
                structured_data_str += f"{data['manual_input']}\n"
            structured_data_str += "\n"

    prompt = f"""
    Analyze the following project and return a structured JSON response.

    ---
    BASIC PROJECT INFO:
    Name: {project.name}
    Description: {project.description}
    Platform: {project.platform}
    Tech Stack: {project.tech_stack}
    Scale: {project.scale}
    Budget: ${project.budget:,.0f}
    Risk Level: {project.risk_level}
    ---
    STRUCTURED PROJECT DETAILS:
    {structured_data_str}
    ---
    """

    raw_response = generate_ai_analysis(prompt)
    ai_data = None
    validation_errors = []

    try:
        ai_data = json.loads(raw_response)
        # Enforce AI JSON Validation
        required_keys = [
            "executive_summary", "architecture", "threat_model", "sdlc",
            "cost_estimation", "testing_plan", "ai_risk_adjustment"
        ]
        missing_keys = [key for key in required_keys if key not in ai_data]
        if missing_keys:
            validation_errors.append(f"AI response missing required keys: {', '.join(missing_keys)}")
    except json.JSONDecodeError:
        validation_errors.append("AI returned an invalid, non-JSON response.")

    # Check if validation failed
    if validation_errors:
        messages.error(request, f"❌ AI analysis failed: {validation_errors[0]}. Please try again.")
        # Optionally log the full error for debugging
        print(f"Failed AI Response: {raw_response}")
        return redirect("dashboard")

    # --- Success Path ---
    messages.success(request, "✅ Analysis generated successfully")

    # Save analysis, now with raw AI response
    analysis = ProjectAnalysis.objects.create(
        project=project,
        user=request.user,
        raw_ai_response=ai_data,  # Persist raw AI output
        executive_summary=ai_data.get("executive_summary", ""),
        architecture=ai_data.get("architecture", ""),
        threat_model=ai_data.get("threat_model", ""),
        sdls_recommendations=ai_data.get("sdlc", ""),  # Map from 'sdlc' key
        cost_estimation=ai_data.get("cost_estimation", ""),
        testing_plan=ai_data.get("testing_plan", ""),
        likelihood=ai_data.get("likelihood_score", 0),
        impact=ai_data.get("impact_score", 0),
        top_risks="\n".join(f"- {risk}" for risk in ai_data.get("key_risks", [])),
        immediate_actions="\n".join(f"- {rec}" for rec in ai_data.get("recommendations", [])),
    )

    # Apply hybrid security scoring
    score, category = calculate_final_security_score(
        project,
        ai_risk_adjustment=ai_data.get("ai_risk_adjustment", 0)
    )
    analysis.security_score = score
    analysis.risk_category = category
    analysis.save()

    return redirect("view_analysis", analysis_id=analysis.id)


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


