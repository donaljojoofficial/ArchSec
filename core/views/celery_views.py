import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from celery import current_app
from core.models.project_analysis import ProjectAnalysis

logger = logging.getLogger(__name__)

@login_required
def celery_dashboard(request):
    inspector = current_app.control.inspect()
    
    active = {}
    scheduled = {}
    reserved = {}
    connection_error = None

    try:
        # Attempt to fetch stats. If Redis is down, this should raise an OperationalError.
        active = inspector.active() or {}
        scheduled = inspector.scheduled() or {}
        reserved = inspector.reserved() or {}
    except Exception as e:
        connection_error = str(e)
        logger.error(f"Celery dashboard connection error: {e}")
    
    # Calculate totals
    total_active = sum(len(tasks) for tasks in active.values()) if active else 0
    total_scheduled = sum(len(tasks) for tasks in scheduled.values()) if scheduled else 0
    total_reserved = sum(len(tasks) for tasks in reserved.values()) if reserved else 0
    
    pending_analyses = ProjectAnalysis.objects.filter(risk_category="Pending").order_by('-created_at')

    return render(request, "core/celery_dashboard.html", {
        "active": active,
        "scheduled": scheduled,
        "reserved": reserved,
        "total_active": total_active,
        "total_scheduled": total_scheduled,
        "total_reserved": total_reserved,
        "pending_analyses": pending_analyses,
        "connection_error": connection_error,
    })