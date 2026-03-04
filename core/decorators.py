"""
Custom decorators for authentication and authorization.
"""

from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from core.services.auth_service import AuthorizationService
import logging

logger = logging.getLogger(__name__)


def admin_required(view_func):
    """
    Decorator to check if user is an admin.
    Redirects to home if user is not an admin.
    """
    @wraps(view_func)
    @login_required(login_url='login')
    def wrapper(request, *args, **kwargs):
        if AuthorizationService.is_admin(request.user):
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'You do not have permission to access this page.')
            logger.warning(f"Unauthorized admin access attempt by user: {request.user.username}")
            return redirect('dashboard')
    return wrapper


def analyst_required(view_func):
    """
    Decorator to check if user is a security analyst or admin.
    Redirects to home if user is not an analyst.
    """
    @wraps(view_func)
    @login_required(login_url='login')
    def wrapper(request, *args, **kwargs):
        if AuthorizationService.is_analyst(request.user) or AuthorizationService.is_admin(request.user):
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'You do not have permission to access this page.')
            logger.warning(f"Unauthorized analyst access attempt by user: {request.user.username}")
            return redirect('dashboard')
    return wrapper


def project_owner_required(view_func):
    """
    Decorator to check if user owns the project.
    Used for views that have project_id in URL parameters.
    """
    @wraps(view_func)
    @login_required(login_url='login')
    def wrapper(request, project_id=None, *args, **kwargs):
        from core.models.project import Project
        from django.shortcuts import get_object_or_404
        
        if project_id is None:
            return view_func(request, *args, **kwargs)
        
        try:
            project = get_object_or_404(Project, id=project_id)
            if AuthorizationService.can_access_project(request.user, project):
                return view_func(request, project_id, *args, **kwargs)
            else:
                messages.error(request, 'You do not have permission to access this project.')
                logger.warning(f"Unauthorized project access attempt by user: {request.user.username} for project: {project_id}")
                return redirect('dashboard')
        except Exception as e:
            logger.error(f"Error in project_owner_required decorator: {str(e)}")
            return HttpResponseForbidden('Access Denied')
    
    return wrapper


def analysis_owner_required(view_func):
    """
    Decorator to check if user owns the analysis.
    Used for views that have analysis_id in URL parameters.
    """
    @wraps(view_func)
    @login_required(login_url='login')
    def wrapper(request, analysis_id=None, *args, **kwargs):
        from core.models.project_analysis import ProjectAnalysis
        from django.shortcuts import get_object_or_404
        
        if analysis_id is None:
            return view_func(request, *args, **kwargs)
        
        try:
            analysis = get_object_or_404(ProjectAnalysis, id=analysis_id)
            if AuthorizationService.can_access_analysis(request.user, analysis):
                return view_func(request, analysis_id, *args, **kwargs)
            else:
                messages.error(request, 'You do not have permission to access this analysis.')
                logger.warning(f"Unauthorized analysis access attempt by user: {request.user.username} for analysis: {analysis_id}")
                return redirect('dashboard')
        except Exception as e:
            logger.error(f"Error in analysis_owner_required decorator: {str(e)}")
            return HttpResponseForbidden('Access Denied')
    
    return wrapper


def permission_required(permission_codename):
    """
    Decorator to check if user has a specific permission.
    
    Args:
        permission_codename (str): The permission codename to check
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required(login_url='login')
        def wrapper(request, *args, **kwargs):
            if AuthorizationService.has_permission(request.user, permission_codename):
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'You do not have permission to perform this action.')
                logger.warning(f"Unauthorized permission access attempt by user: {request.user.username} for permission: {permission_codename}")
                return HttpResponseForbidden('Access Denied')
        return wrapper
    return decorator
