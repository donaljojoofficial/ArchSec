import logging
from django.shortcuts import render
from django.core.cache import cache
from celery import current_app
from core.models.project_analysis import ProjectAnalysis
from core.decorators import admin_required
from core.cache_utils import OPERATIONS_CACHE_TIMEOUT

logger = logging.getLogger(__name__)


@admin_required
def celery_dashboard(request):
    celery_state = cache.get("archsec:operations:celery_state")
    if celery_state is None:
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

        celery_state = {
            "active": active,
            "scheduled": scheduled,
            "reserved": reserved,
            "connection_error": connection_error,
        }
        cache.set("archsec:operations:celery_state", celery_state, OPERATIONS_CACHE_TIMEOUT)
    else:
        active = celery_state["active"]
        scheduled = celery_state["scheduled"]
        reserved = celery_state["reserved"]
        connection_error = celery_state["connection_error"]
    
    # Calculate totals
    total_active = sum(len(tasks) for tasks in active.values()) if active else 0
    total_scheduled = sum(len(tasks) for tasks in scheduled.values()) if scheduled else 0
    total_reserved = sum(len(tasks) for tasks in reserved.values()) if reserved else 0
    
    pending_analyses = ProjectAnalysis.objects.select_related("project").filter(risk_category="Pending").order_by("-created_at")
    failed_analyses = ProjectAnalysis.objects.select_related("project").filter(risk_category="Error").order_by("-created_at")[:10]

    return render(request, "core/celery_dashboard.html", {
        "active": active,
        "scheduled": scheduled,
        "reserved": reserved,
        "total_active": total_active,
        "total_scheduled": total_scheduled,
        "total_reserved": total_reserved,
        "pending_analyses": pending_analyses,
        "failed_analyses": failed_analyses,
        "connection_error": connection_error,
    })
