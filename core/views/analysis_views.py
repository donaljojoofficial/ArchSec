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
import re
                    



# =====================================================
# SECTION EXTRACTOR
# =====================================================
def extract_section(text, header):
    """
    Extract content under a given UPPERCASE header until the next header.
    """
    text = text or ""
    header = header.strip().upper()

    if header not in text:
        return ""

    # Cut everything before header
    section = text.split(header, 1)[1]

    HEADERS = [
        "EXECUTIVE SUMMARY",
        "SYSTEM ARCHITECTURE",
        "THREAT MODEL",
        "SECURE SDLC",
        "COST ESTIMATION",
        "SECURITY TESTING PLAN",
    ]

    # Stop when next header appears
    for h in HEADERS:
        if h != header and h in section:
            section = section.split(h, 1)[0]
            break

    return section.strip()



# =====================================================
# SUB-SECTION EXTRACTOR (Top risks, immediate actions)
# =====================================================
def extract_subsection(text, main_header, keyword):
    """
    Extracts a bullet-point subsection from EXECUTIVE SUMMARY.
    Example:
      extract_subsection(text, "EXECUTIVE SUMMARY", "Top 3 critical risks")
    """
    main_section = extract_section(text, main_header)
    main_lower = main_section.lower()
    keyword_lower = keyword.lower()

    if keyword_lower not in main_lower:
        return ""

    # Extract starting at keyword
    part = main_lower.split(keyword_lower, 1)[1]

    # Limit by next sentence or next bullet
    stops = ["- ", "•", "\n\n", "immediate actions", "overall"]
    for stop in stops:
        if stop in part:
            part = part.split(stop, 1)[0]
            break

    return part.strip().lstrip("-•").strip()

def extract_score(text, label):
    match = re.search(rf"{label}\s*[:\-]\s*(\d)", text, re.IGNORECASE)
    return int(match.group(1)) if match else 0


# =====================================================
# GENERATE ANALYSIS
# =====================================================
@login_required
def generate_analysis(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)

    # Prepare structured data for the prompt
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
You are a Senior Secure Software Architect AI. Generate a fully structured and highly technical secure system analysis for the following project.

Use the structured details as the primary source of truth. The basic project info is for context.

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

OUTPUT REQUIREMENTS:
Use the following EXACT SECTION HEADERS in markdown:

EXECUTIVE SUMMARY
SYSTEM ARCHITECTURE
THREAT MODEL
SECURE SDLC RECOMMENDATIONS
COST ESTIMATION
SECURITY TESTING PLAN

EXECUTIVE SUMMARY MUST INCLUDE:
- Overall security posture (1–2 sentences)
- Top 3 Critical Risks (bullet points)
- Immediate Security Actions Required (bullet points)

SYSTEM ARCHITECTURE MUST INCLUDE:
- Logical architecture based on the structured data provided.
- Data flow overview.
- Trust boundaries.
- Authentication & authorization model.

THREAT MODEL MUST INCLUDE:
- STRIDE breakdown.
- Relevant OWASP Top 10 risks.
- Attack surface summary.

SECURE SDLC RECOMMENDATIONS MUST INCLUDE:
- Phase-wise practices.
- Mandatory security gates.
- Required tools (SAST, DAST, SCA).

COST ESTIMATION MUST INCLUDE:
- Security cost impact (low/medium/high).
- Resource estimation for implementation.

SECURITY TESTING PLAN MUST INCLUDE:
- Pentesting scope.
- Automated testing tools.
- Continuous security monitoring suggestions.

Provide two numerical scores at the very end:
LIKELIHOOD SCORE (1–5)
IMPACT SCORE (1–5)
"""

    generated_text = generate_ai_analysis(prompt)

    likelihood = extract_score(generated_text, "LIKELIHOOD SCORE")
    impact = extract_score(generated_text, "IMPACT SCORE")

    # Extract top-level sections
    executive_summary = extract_section(generated_text, "EXECUTIVE SUMMARY")
    architecture = extract_section(generated_text, "SYSTEM ARCHITECTURE")
    threat_model = extract_section(generated_text, "THREAT MODEL")
    sdls_recommendations = extract_section(generated_text, "SECURE SDLC RECOMMENDATIONS")
    cost_estimation = extract_section(generated_text, "COST ESTIMATION")
    testing_plan = extract_section(generated_text, "SECURITY TESTING PLAN")

    # Extract subsections from EXECUTIVE SUMMARY
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

        likelihood=likelihood,
        impact=impact,
    )

    # Apply hybrid security scoring
    score, category = calculate_final_security_score(project)
    analysis.security_score = score
    analysis.risk_category = category
    analysis.save()

    messages.success(request, f"Security analysis generated — Risk rating: {category} ({score})")

    return redirect("view_analysis", analysis_id=analysis.id)



# =====================================================
# VIEW ANALYSIS
# =====================================================
@login_required
def view_analysis(request, analysis_id):
    analysis = get_object_or_404(ProjectAnalysis, id=analysis_id, user=request.user)
    return render(request, "core/view_analysis.html", {
        "analysis": analysis,
        "project": analysis.project
    })



# =====================================================
# ANALYSIS HISTORY
# =====================================================
@login_required
def history_analysis(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    analyses = ProjectAnalysis.objects.filter(project=project).order_by("-created_at")

    scores = [a.security_score for a in analyses if a.security_score > 0]

    trend_data = {
        "highest": max(scores) if scores else 0,
        "lowest": min(scores) if scores else 0,
        "average": sum(scores)/len(scores) if scores else 0,
        "improving": scores[-1] < scores[0] if len(scores) > 1 else False,
    }

    return render(request, "core/analysis_history.html", {
        "project": project,
        "analyses": analyses,
        "trend": trend_data
    })



# =====================================================
# EXPORT PDF
# =====================================================
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


