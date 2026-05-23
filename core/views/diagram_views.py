from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import ProjectAnalysis
from core.services.auth_service import AuthorizationService
from core.decorators import analysis_owner_required
import logging

logger = logging.getLogger(__name__)

@analysis_owner_required
def view_diagrams(request, analysis_id):
    """
    View diagrams for a specific analysis.
    Only the analysis owner or admin can view it.
    """
    analysis = get_object_or_404(ProjectAnalysis, id=analysis_id)
    
    return render(request, 'core/view_diagrams.html', {'analysis': analysis})
