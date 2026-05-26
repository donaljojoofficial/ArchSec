import hashlib
import json

from django.core.cache import cache


PUBLIC_PAGE_TIMEOUT = 60 * 15
USER_DATA_TIMEOUT = 60 * 5
ANALYSIS_FORMAT_TIMEOUT = 60 * 30
OPERATIONS_CACHE_TIMEOUT = 10


def user_dashboard_key(user_id):
    return f"archsec:user:{user_id}:dashboard"


def unread_notifications_key(user_id):
    return f"archsec:user:{user_id}:unread_notifications"


def notification_list_key(user_id):
    return f"archsec:user:{user_id}:notification_list"


def analysis_format_key(analysis, section):
    version_source = {
        "id": analysis.id,
        "risk_category": analysis.risk_category,
        "security_score": analysis.security_score,
        "raw_ai_response": analysis.raw_ai_response,
        "architecture": analysis.architecture,
        "threat_model": analysis.threat_model,
        "sdls_recommendations": analysis.sdls_recommendations,
        "cost_estimation": analysis.cost_estimation,
        "testing_plan": analysis.testing_plan,
    }
    version = hashlib.sha256(
        json.dumps(version_source, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()[:16]
    return f"archsec:analysis:{analysis.id}:{version}:{section}"


def invalidate_user_cache(user_id):
    if user_id:
        cache.delete_many([
            user_dashboard_key(user_id),
            unread_notifications_key(user_id),
            notification_list_key(user_id),
        ])


def invalidate_analysis_cache(analysis_id):
    # Analysis formatting keys include a content hash, so old keys naturally fall
    # out by timeout. This marker gives callers a central invalidation hook.
    if analysis_id:
        cache.delete(f"archsec:analysis:{analysis_id}:marker")
