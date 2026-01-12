from core.models.project import Project
from core.services.ai_client import generate_ai_analysis
import json

def calculate_rule_score(project: Project):
    score = 0
    structured_data = project.structured_data or {}

    # --- Risk level weight ---
    risk_weights = {"low": 10, "medium": 40, "high": 70}
    score += risk_weights.get(project.risk_level, 20)

    # --- Platform exposure weighting ---
    platform_weights = {"api": 20, "cloud": 20, "iot": 25, "mobile": 10, "web": 10, "other": 5}
    score += platform_weights.get(project.platform, 5)

    # --- Scale weighting ---
    scale_weights = {"small": 5, "medium": 10, "large": 20}
    score += scale_weights.get(project.scale.lower(), 10)

    # --- Budget adequacy scoring ---
    expected_budget = 0
    if project.scale.lower() == "small":
        expected_budget = 20000
    elif project.scale.lower() == "medium":
        expected_budget = 50000
    elif project.scale.lower() == "large":
        expected_budget = 120000

    if project.budget < expected_budget:
        score += 20  # underfunded increases risk
    else:
        score -= 10  # adequate budget reduces risk

    # --- Structured Data Penalties & Rewards ---
    # Penalize missing critical sections
    for section in ['security', 'monitoring', 'compliance']:
        if not structured_data.get(section):
            score += 15

    # Reward mature architecture, penalize monolith
    architecture = structured_data.get('architecture', {}).get('options', [])
    if 'monolith' in architecture:
        score += 5
    if 'microservices' in architecture or 'serverless' in architecture:
        score -= 10

    # Penalize missing key security controls
    security_controls = structured_data.get('security', {}).get('options', [])
    for control in ['authentication', 'authorization', 'encryption']:
        if control not in security_controls:
            score += 10

    # Clamp baseline score range
    return max(0, min(score, 100))


def get_ai_risk_adjustment(project: Project):
    structured_data_str = json.dumps(project.structured_data, indent=2)

    prompt = f"""
As a security risk analyst, rate the overall security risk of this system on a scale of 1-10, where 10 is the highest risk.
Consider BOTH the basic info and the detailed structured data. The structured data provides the most important clues.
Return ONLY a single number (1-10).

---
BASIC PROJECT INFO:
Name: {project.name}
Description: {project.description}
Platform: {project.platform}
Risk Level: {project.risk_level}
Scale: {project.scale}
---
STRUCTURED PROJECT DETAILS:
{structured_data_str}
---

Return ONLY a single number (1-10).
"""

    response = generate_ai_analysis(prompt)

    try:
        ai_value = int("".join(filter(str.isdigit, response)))
        return max(1, min(ai_value, 10))
    except (ValueError, TypeError):
        return 5  # Fallback to a neutral score if AI fails


def determine_risk_category(score: int):
    if score >= 70:
        return "High Risk"
    elif score >= 40:
        return "Medium Risk"
    return "Low Risk"


def calculate_final_security_score(project: Project):
    base_score = calculate_rule_score(project)
    ai_adjustment = get_ai_risk_adjustment(project)

    # AI adjustment has a stronger effect now
    final_score = base_score + (ai_adjustment * 3)

    # Final hard clamp
    final_score = max(0, min(final_score, 100))

    category = determine_risk_category(final_score)

    return final_score, category
