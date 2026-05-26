from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import ProjectAnalysis
from core.services.auth_service import AuthorizationService
from core.decorators import analysis_owner_required
from core.tasks import fallback_diagrams
import logging

logger = logging.getLogger(__name__)

@analysis_owner_required
def view_diagrams(request, analysis_id):
    """
    View diagrams for a specific analysis.
    Only the analysis owner or admin can view it.
    """
    analysis = get_object_or_404(ProjectAnalysis.objects.select_related("project"), id=analysis_id)
    fallbacks = fallback_diagrams(analysis.project)
    diagram_fields = {
        "uml_diagram": "future_state_diagram",
        "dfd_diagram": "current_state_diagram",
        "erd_diagram": "ai_integration_flow_diagram",
        "threat_diagram": "deployment_flow_diagram",
        "security_testing_diagram": "security_testing_flow_diagram",
        "migration_roadmap_diagram": "migration_roadmap_diagram",
    }
    for field_name, fallback_name in diagram_fields.items():
        if not getattr(analysis, field_name):
            setattr(analysis, field_name, fallbacks[fallback_name])
    
    return render(request, 'core/view_diagrams.html', {'analysis': analysis})
