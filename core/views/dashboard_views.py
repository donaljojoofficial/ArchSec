from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import Project

MODERNIZATION_SECTIONS = [
    'current_backend',
    'current_frontend',
    'cms_framework',
    'database',
    'hosting',
    'deployment',
    'runtime_age',
    'testing_process',
    'security_testing_process',
    'observability_operations',
    'backups_incident_response',
    'ai_readiness',
    'migration_constraints',
]

CRITICAL_MODERNIZATION_SECTIONS = [
    'current_backend',
    'current_frontend',
    'database',
    'hosting',
    'deployment',
    'runtime_age',
    'testing_process',
    'security_testing_process',
    'observability_operations',
    'ai_readiness',
    'migration_constraints',
]

SECTION_LABELS = {
    'current_backend': 'backend',
    'current_frontend': 'frontend',
    'cms_framework': 'CMS/framework',
    'database': 'database',
    'hosting': 'hosting',
    'deployment': 'deployment',
    'runtime_age': 'runtime age',
    'testing_process': 'testing process',
    'security_testing_process': 'security testing',
    'observability_operations': 'observability',
    'backups_incident_response': 'backups/incident response',
    'ai_readiness': 'AI readiness',
    'migration_constraints': 'migration constraints',
}

@login_required
def dashboard(request):
    projects = Project.objects.filter(user=request.user).order_by('-created_at')

    for project in projects:
        structured_data = project.structured_data or {}
        filled_sections = [
            section for section in MODERNIZATION_SECTIONS
            if structured_data.get(section)
        ]
        project.completeness_percentage = (
            len(filled_sections) / len(MODERNIZATION_SECTIONS)
        ) * 100

        missing = [
            SECTION_LABELS[section]
            for section in CRITICAL_MODERNIZATION_SECTIONS
            if section not in structured_data
        ]
        project.missing_critical = missing

    return render(request, "core/dashboard.html", {"projects": projects})
