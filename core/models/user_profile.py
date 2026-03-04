from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Extended user profile for additional information and settings.
    """
    ROLE_CHOICES = [
        ('user', 'Regular User'),
        ('admin', 'Administrator'),
        ('analyst', 'Security Analyst'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    bio = models.TextField(blank=True, null=True, help_text="User biography")
    avatar_url = models.URLField(blank=True, null=True, help_text="User avatar URL")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    organization = models.CharField(max_length=255, blank=True, null=True)
    
    # Security & Account settings
    two_factor_enabled = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    last_login_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username} Profile"

    @property
    def is_admin(self):
        return self.role == 'admin' or self.user.is_staff

    @property
    def is_analyst(self):
        return self.role == 'analyst' or self.user.is_staff


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a user profile when a new user is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile when user is saved."""
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)
