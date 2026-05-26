from django.core.cache import cache

from core.cache_utils import ANALYSIS_FORMAT_TIMEOUT, analysis_format_key


def as_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def get_raw_response(analysis):
    raw_response = analysis.raw_ai_response
    if isinstance(raw_response, list):
        for item in raw_response:
            if isinstance(item, dict):
                raw_response = item
                break
        else:
            return {}
    if not isinstance(raw_response, dict):
        return {}

    for key in ("assessment", "analysis", "modernization_assessment", "result", "data"):
        nested = raw_response.get(key)
        if isinstance(nested, dict):
            return nested
    return raw_response


def get_findings(analysis):
    cache_key = analysis_format_key(analysis, "findings")
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    raw_response = get_raw_response(analysis)
    findings = raw_response.get("findings", [])
    if not isinstance(findings, list):
        findings = []

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
    if normalized:
        cache.set(cache_key, normalized, ANALYSIS_FORMAT_TIMEOUT)
        return normalized

    fallback_sections = [
        ("Architecture", "Modern architecture proposal", analysis.architecture),
        ("Security", "Security and technical debt risks", analysis.threat_model),
        ("Process", "Development and DevOps improvements", analysis.sdls_recommendations),
        ("Cost", "Cost and requirements", analysis.cost_estimation),
        ("Testing", "Testing and security validation workflow", analysis.testing_plan),
    ]
    for category, title, text in fallback_sections:
        if not text:
            continue
        normalized.append({
            "title": title,
            "category": category,
            "current_issue": text,
            "why_it_matters": "This area affects modernization risk, delivery confidence, and operational reliability.",
            "recommended_solution": text,
            "tools_services": [],
            "cost_estimate": "",
            "effort": "",
            "required_skills": [],
            "migration_steps": [],
            "dependencies": [],
            "risks": [],
            "mitigations": [],
            "expected_benefits": [],
            "priority": "High" if category in ("Architecture", "Security") else "Medium",
        })
    cache.set(cache_key, normalized, ANALYSIS_FORMAT_TIMEOUT)
    return normalized


def get_scorecards(analysis):
    cache_key = analysis_format_key(analysis, "scorecards")
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    raw_response = get_raw_response(analysis)
    modernization_score = raw_response.get("modernization_score")
    if modernization_score is None:
        modernization_score = analysis.security_score
    scorecards = {
        "modernization_score": modernization_score,
        "ai_readiness_score": raw_response.get("ai_readiness_score"),
        "technical_debt_score": raw_response.get("technical_debt_score"),
        "security_risk_score": raw_response.get("security_risk_score"),
        "migration_risk_score": raw_response.get("migration_risk_score"),
    }
    cache.set(cache_key, scorecards, ANALYSIS_FORMAT_TIMEOUT)
    return scorecards


def get_roadmap(analysis):
    cache_key = analysis_format_key(analysis, "roadmap")
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    roadmap = as_list(get_raw_response(analysis).get("roadmap"))
    cache.set(cache_key, roadmap, ANALYSIS_FORMAT_TIMEOUT)
    return roadmap


def get_quick_wins(analysis):
    cache_key = analysis_format_key(analysis, "quick_wins")
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    quick_wins = as_list(get_raw_response(analysis).get("quick_wins"))
    cache.set(cache_key, quick_wins, ANALYSIS_FORMAT_TIMEOUT)
    return quick_wins
