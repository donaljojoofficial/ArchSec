from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models.project import Project
from core.models.project_analysis import ProjectAnalysis
from core.services.ai_client import generate_ai_analysis
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from core.services.security_scoring import calculate_final_security_score
from django.contrib import messages


# -------------------------------
# Section Extractor
# -------------------------------
def extract_section(text, header):
    """
    Extract content under a section header until the next known header.
    """
    if header not in text:
        return ""

    section = text.split(header, 1)[1]

    NEXT_HEADERS = [
        "EXECUTIVE SUMMARY",
        "SYSTEM ARCHITECTURE",
        "THREAT MODEL",
        "SECURE SDLC",
        "COST ESTIMATION",
        "SECURITY TESTING PLAN",
    ]

    for next_header in NEXT_HEADERS:
        if next_header in section and next_header != header:
            section = section.split(next_header, 1)[0]
            break

    if subsection in block:
        sub = block.split(subsection, 1)[1]

        # end at next subsection if exists
        for end_key in ["Top Risks", "Immediate Actions"]:
            if end_key in sub and end_key != subsection:
                sub = sub.split(end_key, 1)[0]
                break

        return sub.strip()    

    return section.strip()


# -------------------------------
# Generate Analysis
# -------------------------------
@login_required
def generate_analysis(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)

    # Enhanced prompt with EXECUTIVE SUMMARY section
    prompt = f"""
You are a security architect AI. Generate a structured secure system analysis for the following project:

Name: {project.name}
Description: {project.description}
Platform: {project.platform}
Tech Stack: {project.tech_stack}
Scale: {project.scale}
Budget: {project.budget}
Risk Level: {project.risk_level}

Your response must contain sections with EXACT HEADERS:

EXECUTIVE SUMMARY
SYSTEM ARCHITECTURE
THREAT MODEL
SECURE SDLC
COST ESTIMATION
SECURITY TESTING PLAN

EXECUTIVE SUMMARY must include:
- Overall security posture (1–2 sentences)
- Top 3 critical risks
- Immediate actions recommended

Make sure each section begins with its header in uppercase.
"""

    generated_text = generate_ai_analysis(prompt)

    # Extract sections
    executive_summary = extract_section(generated_text, "EXECUTIVE SUMMARY")
    architecture = extract_section(generated_text, "SYSTEM ARCHITECTURE")
    threat_model = extract_section(generated_text, "THREAT MODEL")
    sdls_recommendations = extract_section(generated_text, "SECURE SDLC")
    cost_estimation = extract_section(generated_text, "COST ESTIMATION")
    testing_plan = extract_section(generated_text, "SECURITY TESTING PLAN")
    # Extract executive summary and sub-sections
    top_risks = extract_subsection(generated_text, "EXECUTIVE SUMMARY", "Top 3 critical risks")
    immediate_actions = extract_subsection(generated_text, "EXECUTIVE SUMMARY", "Immediate actions recommended")


    # Save analysis
    analysis = ProjectAnalysis.objects.create(
    project=project,
    user=request.user,

    executive_summary=executive_summary,
    top_risks=top_risks,
    immediate_actions=immediate_actions,

    architecture=architecture,
    threat_model=threat_model,
    cost_estimation=cost_estimation,
    sdls_recommendations=sdls_recommendations,
    testing_plan=testing_plan,
    )


    # Apply hybrid security scoring
    score, category = calculate_final_security_score(project)
    analysis.security_score = score
    analysis.risk_category = category
    analysis.save()

    messages.success(request, f"Security analysis generated — Risk rating: {category} ({score})")

    return redirect("view_analysis", analysis_id=analysis.id)


# -------------------------------
# View Single Analysis
# -------------------------------
@login_required
def view_analysis(request, analysis_id):
    analysis = get_object_or_404(ProjectAnalysis, id=analysis_id, user=request.user)
    return render(request, "core/view_analysis.html", {
        "analysis": analysis,
        "project": analysis.project
    })


# -------------------------------
# Analysis History
# -------------------------------
@login_required
def history_analysis(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)

    analyses = ProjectAnalysis.objects.filter(project=project).order_by("-created_at")
    scores = [a.security_score for a in analyses if a.security_score > 0]

    trend_data = {
        "highest": max(scores) if scores else 0,
        "lowest": min(scores) if scores else 0,
        "average": sum(scores)/len(scores) if scores else 0,
        "improving": scores[-1] < scores[0] if len(scores) > 1 else False
    }

    return render(request, "core/analysis_history.html", {
        "project": project,
        "analyses": analyses,
        "trend": trend_data
    })


# -------------------------------
# Export PDF
# -------------------------------
@login_required
def download_analysis_pdf(request, analysis_id):
    analysis = get_object_or_404(ProjectAnalysis, id=analysis_id, user=request.user)
    project = analysis.project

    html_content = render_to_string("core/analysis_pdf.html", {
        "analysis": analysis,
        "project": project
    })

    pdf_file = HTML(string=html_content).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=\"analysis_{analysis_id}.pdf\"'
    return response


