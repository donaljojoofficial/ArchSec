def as_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def get_raw_response(analysis):
    return analysis.raw_ai_response if isinstance(analysis.raw_ai_response, dict) else {}


def get_findings(analysis):
    raw_response = get_raw_response(analysis)
    findings = raw_response.get("findings", [])
    if not isinstance(findings, list):
        return []

    normalized = []
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        normalized.append({
            "title": finding.get("title") or "Modernization finding",
            "category": finding.get("category") or "General",
            "current_issue": finding.get("current_issue") or "",
            "why_it_matters": finding.get("why_it_matters") or finding.get("impact") or "",
            "recommended_solution": finding.get("recommended_solution") or finding.get("recommendation") or "",
            "tools_services": as_list(finding.get("tools_services")),
            "cost_estimate": finding.get("cost_estimate") or "",
            "effort": finding.get("effort") or "",
            "required_skills": as_list(finding.get("required_skills")),
            "migration_steps": as_list(finding.get("migration_steps")),
            "dependencies": as_list(finding.get("dependencies")),
            "risks": as_list(finding.get("risks")),
            "mitigations": as_list(finding.get("mitigations")),
            "expected_benefits": as_list(finding.get("expected_benefits")),
            "priority": finding.get("priority") or "Medium",
        })
    return normalized


def get_scorecards(analysis):
    raw_response = get_raw_response(analysis)
    modernization_score = raw_response.get("modernization_score")
    if modernization_score is None:
        modernization_score = analysis.security_score
    return {
        "modernization_score": modernization_score,
        "ai_readiness_score": raw_response.get("ai_readiness_score"),
        "technical_debt_score": raw_response.get("technical_debt_score"),
        "security_risk_score": raw_response.get("security_risk_score"),
        "migration_risk_score": raw_response.get("migration_risk_score"),
    }


def get_roadmap(analysis):
    return as_list(get_raw_response(analysis).get("roadmap"))


def get_quick_wins(analysis):
    return as_list(get_raw_response(analysis).get("quick_wins"))
