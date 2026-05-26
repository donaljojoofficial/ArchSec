from .models.notification import Notification
from .cache_utils import USER_DATA_TIMEOUT, unread_notifications_key
from django.core.cache import cache

def notifications(request):
    if request.user.is_authenticated:
        cache_key = unread_notifications_key(request.user.id)
        unread_notifications = cache.get(cache_key)
        if unread_notifications is None:
            unread_notifications = list(
                Notification.objects
                .filter(user=request.user, is_read=False)
                .order_by('-created_at')
                .values("id", "message", "link", "created_at")[:10]
            )
            cache.set(cache_key, unread_notifications, USER_DATA_TIMEOUT)
        return {'unread_notifications': unread_notifications}
    return {}
