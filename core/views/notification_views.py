from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from core.models.notification import Notification
import logging

logger = logging.getLogger(__name__)

@login_required(login_url='login')
def notification_list(request):
    """
    Display all notifications for the logged-in user.
    """
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/notification_list.html', {'notifications': notifications})

@login_required(login_url='login')
def mark_notification_as_read(request, notification_id):
    """
    Mark a specific notification as read.
    Only the notification owner can mark it as read.
    """
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        messages.success(request, 'Notification marked as read.')
        logger.info(f"Notification {notification_id} marked as read by user: {request.user.username}")
        
        if notification.link:
            return redirect(notification.link)
        return redirect('notifications')
    except Notification.DoesNotExist:
        messages.error(request, 'Notification not found or access denied.')
        logger.warning(f"User {request.user.username} attempted to access notification {notification_id} they don't own.")
        raise Http404("Notification not found")

@login_required(login_url='login')
def clear_all_notifications(request):
    """
    Clear all notifications for the logged-in user.
    """
    count = Notification.objects.filter(user=request.user).count()
    Notification.objects.filter(user=request.user).delete()
    messages.success(request, f'Cleared {count} notification(s).')
    logger.info(f"User {request.user.username} cleared all notifications.")
    return redirect('notifications')
