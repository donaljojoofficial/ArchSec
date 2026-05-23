from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Project, UserProfile, ProjectAnalysis, Notification


# ========================
# User and Profile Admin
# ========================

class UserProfileInline(admin.StackedInline):
    """
    Inline admin for UserProfile to manage within User admin.
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('role', 'organization', 'phone_number', 'bio', 'two_factor_enabled', 'is_verified', 'email_notifications', 'last_login_ip', 'last_login_time')
    readonly_fields = ('last_login_ip', 'last_login_time')


class UserAdmin(BaseUserAdmin):
    """
    Enhanced User admin with profile information.
    """
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'get_user_role', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined', 'profile__role')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    
    def get_user_role(self, obj):
        """Display user role from profile."""
        return obj.profile.get_role_display() if hasattr(obj, 'profile') else 'N/A'
    get_user_role.short_description = 'Role'


# Unregister the default User admin and register our enhanced version
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin for UserProfile model.
    """
    list_display = ('user', 'role', 'organization', 'is_verified', 'two_factor_enabled', 'created_at', 'updated_at')
    list_filter = ('role', 'is_verified', 'two_factor_enabled', 'created_at')
    search_fields = ('user__username', 'user__email', 'organization')
    readonly_fields = ('created_at', 'updated_at', 'last_login_ip', 'last_login_time')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Profile Information', {
            'fields': ('role', 'organization', 'phone_number', 'bio')
        }),
        ('Avatar', {
            'fields': ('avatar_url',),
            'classes': ('collapse',)
        }),
        ('Security', {
            'fields': ('is_verified', 'two_factor_enabled', 'email_notifications'),
            'classes': ('collapse',)
        }),
        ('Activity', {
            'fields': ('last_login_ip', 'last_login_time', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


admin.site.register(UserProfile, UserProfileAdmin)


# ========================
# Project Admin
# ========================

class ProjectAdmin(admin.ModelAdmin):
    """
    Admin for Project model.
    """
    list_display = ('name', 'user', 'platform', 'risk_level', 'budget', 'created_at')
    list_filter = ('platform', 'risk_level', 'created_at')
    search_fields = ('name', 'description', 'user__username')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Project Information', {
            'fields': ('user', 'name', 'description', 'platform')
        }),
        ('Technical Details', {
            'fields': ('tech_stack', 'scale', 'risk_level')
        }),
        ('Budget', {
            'fields': ('budget',)
        }),
        ('Data', {
            'fields': ('structured_data', 'system_design_data'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Ensure user is set when creating project."""
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Project, ProjectAdmin)


# ========================
# Project Analysis Admin
# ========================

class ProjectAnalysisAdmin(admin.ModelAdmin):
    """
    Admin for ProjectAnalysis model.
    """
    list_display = ('id', 'project', 'user', 'risk_category', 'security_score', 'created_at')
    list_filter = ('risk_category', 'security_score', 'created_at', 'user')
    search_fields = ('project__name', 'user__username')
    readonly_fields = ('task_id', 'created_at', 'raw_ai_response')
    
    fieldsets = (
        ('Analysis Information', {
            'fields': ('project', 'user', 'task_id')
        }),
        ('Security Assessment', {
            'fields': ('risk_category', 'security_score', 'impact', 'likelihood')
        }),
        ('Analysis Content', {
            'fields': ('architecture', 'threat_model', 'sdls_recommendations', 'cost_estimation', 'testing_plan'),
            'classes': ('collapse',)
        }),
        ('Executive Summary', {
            'fields': ('executive_summary', 'critical_risks', 'top_risks', 'immediate_actions'),
            'classes': ('collapse',)
        }),
        ('Diagrams', {
            'fields': ('uml_diagram', 'dfd_diagram', 'erd_diagram', 'threat_diagram'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'raw_ai_response'),
            'classes': ('collapse',)
        }),
    )


admin.site.register(ProjectAnalysis, ProjectAnalysisAdmin)


# ========================
# Notification Admin
# ========================

class NotificationAdmin(admin.ModelAdmin):
    """
    Admin for Notification model.
    """
    list_display = ('id', 'user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')
    readonly_fields = ('created_at',)


admin.site.register(Notification, NotificationAdmin)


# ========================
# Admin Site Configuration
# ========================

admin.site.site_header = "ArchSec Administration"
admin.site.site_title = "ArchSec Admin"
admin.site.index_title = "Welcome to ArchSec Administration"

