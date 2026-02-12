import logging
from django.http import JsonResponse
from django.db import connection
from celery import current_app

logger = logging.getLogger(__name__)

def health_check(request):
    health_status = {
        "status": "ok",
        "components": {
            "database": "unknown",
            "celery_broker": "unknown"
        }
    }
    status_code = 200

    # 1. Check Database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_status["components"]["database"] = "healthy"
    except Exception as e:
        logger.error(f"Health check failed - Database: {e}")
        health_status["components"]["database"] = "unhealthy"
        health_status["status"] = "error"
        status_code = 503

    # 2. Check Celery Broker (Redis)
    try:
        with current_app.connection_or_acquire() as conn:
            conn.ensure_connection(max_retries=1)
            health_status["components"]["celery_broker"] = "healthy"
    except Exception as e:
        logger.error(f"Health check failed - Celery Broker: {e}")
        health_status["components"]["celery_broker"] = "unhealthy"
        health_status["status"] = "error"
        status_code = 503

    return JsonResponse(health_status, status=status_code)