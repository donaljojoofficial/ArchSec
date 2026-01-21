from celery import shared_task
from django.urls import reverse

from .services.ai_client import generate_ai_analysis
from .models import Project, ProjectAnalysis
from .models.notification import Notification
from .services.security_scoring import calculate_final_security_score

@shared_task
def generate_analysis_task(analysis_id):
    """
    Celery task to generate AI analysis for a project.
    """
    try:
        analysis = ProjectAnalysis.objects.get(id=analysis_id)
        project = analysis.project
        
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
        Analyze the following project in detail and return a comprehensive, structured JSON response. 
        For each text section, provide at least three detailed paragraphs.
        
        The JSON response must have the following keys:
        - "executive_summary": (string) A detailed summary of the project's security posture.
        - "architecture": (string) A detailed description of the proposed secure architecture.
        - "threat_model": (string) A comprehensive threat model based on STRIDE, listing potential threats.
        - "secure_sdlc": (string) Detailed recommendations for a secure software development lifecycle.
        - "cost_estimation": (string) A detailed breakdown of estimated costs for security measures.
        - "testing_plan": (string) A comprehensive plan for security testing, including tools and methodologies.
        - "key_risks": (array of strings) A list of the top 5-10 key risks.
        - "recommendations": (array of strings) A list of actionable recommendations to mitigate risks.
        - "likelihood_score": (integer, 1-5) An integer representing the likelihood of a breach.
        - "impact_score": (integer, 1-5) An integer representing the impact of a breach.
        - "ai_risk_adjustment": (integer, -10 to 10) An integer to adjust the risk score based on nuances not captured by other fields.

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

        success, ai_response = generate_ai_analysis(prompt)

        analysis.raw_ai_response = ai_response
        
        if success:
            analysis.executive_summary=ai_response.get("executive_summary", "")
            analysis.architecture=ai_response.get("architecture", "")
            analysis.threat_model=ai_response.get("threat_model", "")
            analysis.sdls_recommendations=ai_response.get("secure_sdlc", "")
            analysis.cost_estimation=ai_response.get("cost_estimation", "")
            analysis.testing_plan=ai_response.get("testing_plan", "")
            analysis.likelihood=ai_response.get("likelihood_score", 0)
            analysis.impact=ai_response.get("impact_score", 0)
            analysis.top_risks="\n".join(f"- {risk}" for risk in ai_response.get("key_risks", []))
            analysis.immediate_actions="\n".join(f"- {rec}" for rec in ai_response.get("recommendations", []))

            score, category = calculate_final_security_score(
                project,
                ai_risk_adjustment=ai_response.get("ai_risk_adjustment", 0)
            )
            analysis.security_score = score
            analysis.risk_category = category
            message = f"✅ Your security analysis for project '{project.name}' is complete."
        else:
            analysis.risk_category = "Error"
            message = f"❌ There was an error generating the analysis for project '{project.name}'."

        analysis.save()
        
        Notification.objects.create(
            user=project.user,
            message=message,
            link=reverse("view_analysis", args=[analysis.id]),
        )

        return analysis.id
    except ProjectAnalysis.DoesNotExist:
        # Handle project not found
        return None
    except Exception as e:
        # Handle other exceptions
        if 'analysis' in locals():
            analysis.risk_category = "Error"
            analysis.save()
            message = f"❌ An unexpected error occurred during the analysis for project '{analysis.project.name}'."
            Notification.objects.create(
                user=analysis.project.user,
                message=message,
                link=reverse("view_analysis", args=[analysis.id]),
            )
        return str(e)
