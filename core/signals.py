from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from core.cache_utils import invalidate_analysis_cache, invalidate_user_cache
from core.models import Notification, Project, ProjectAnalysis


@receiver([post_save, post_delete], sender=Project)
def clear_project_owner_cache(sender, instance, **kwargs):
    invalidate_user_cache(instance.user_id)


@receiver([post_save, post_delete], sender=ProjectAnalysis)
def clear_analysis_related_cache(sender, instance, **kwargs):
    invalidate_analysis_cache(instance.id)
    invalidate_user_cache(instance.user_id)


@receiver([post_save, post_delete], sender=Notification)
def clear_notification_owner_cache(sender, instance, **kwargs):
    invalidate_user_cache(instance.user_id)
