from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import Project

@login_required
def dashboard(request):
    projects = Project.objects.filter(user=request.user).order_by('-created_at')

    total_sections = [
        'requirements', 'users', 'architecture', 'technology', 'security',
        'performance', 'database', 'testing', 'deployment', 'monitoring',
        'compliance', 'privacy', 'scalability', 'infrastructure',
        'legacy_constraints', 'ai_readiness'
    ]
    critical_sections = ['security', 'monitoring', 'deployment', 'testing', 'legacy_constraints', 'ai_readiness']

    for project in projects:
        if project.structured_data:
            filled_sections = len(project.structured_data)
            project.completeness_percentage = (filled_sections / len(total_sections)) * 100

            missing = [s for s in critical_sections if s not in project.structured_data]
            project.missing_critical = missing
        else:
            project.completeness_percentage = 0
            project.missing_critical = critical_sections

    return render(request, "core/dashboard.html", {"projects": projects})
