from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import ProjectAnalysis

@login_required
def view_diagrams(request, analysis_id):
    analysis = get_object_or_404(ProjectAnalysis, id=analysis_id)
    return render(request, 'core/view_diagrams.html', {'analysis': analysis})