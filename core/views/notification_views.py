from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.models.notification import Notification

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/notification_list.html', {'notifications': notifications})

@login_required
def mark_notification_as_read(request, notification_id):
    notification = Notification.objects.get(id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    if notification.link:
        return redirect(notification.link)
    return redirect('notifications')

@login_required
def clear_all_notifications(request):
    Notification.objects.filter(user=request.user).delete()
    return redirect('notifications')
