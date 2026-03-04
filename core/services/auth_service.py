"""
Authentication and authorization service module.
Handles user authentication, password management, and permission checks.
"""

import logging
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.utils.timezone import now
from core.models import UserProfile

logger = logging.getLogger(__name__)


class AuthenticationService:
    """
    Service for handling authentication-related operations.
    """

    @staticmethod
    def validate_password_strength(password):
        """
        Validate password strength.
        
        Args:
            password (str): The password to validate
            
        Returns:
            tuple: (is_valid, message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long."
        if password.isdigit():
            return False, "Password cannot be entirely numeric."
        if not any(char.isupper() for char in password):
            return False, "Password must contain at least one uppercase letter."
        if not any(char.isdigit() for char in password):
            return False, "Password must contain at least one digit."
        return True, "Password is strong."

    @staticmethod
    def create_user(username, email, password, first_name="", last_name=""):
        """
        Create a new user with validation.
        
        Args:
            username (str): Username
            email (str): Email address
            password (str): Password
            first_name (str): User's first name
            last_name (str): User's last name
            
        Returns:
            tuple: (user, error_message)
        """
        try:
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                return None, "Username already exists."
            if User.objects.filter(email=email).exists():
                return None, "Email already registered."

            # Validate password strength
            is_valid, message = AuthenticationService.validate_password_strength(password)
            if not is_valid:
                return None, message

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            logger.info(f"New user created: {username}")
            return user, None

        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return None, f"Error creating user: {str(e)}"

    @staticmethod
    def change_password(user, old_password, new_password):
        """
        Change user password.
        
        Args:
            user (User): The user object
            old_password (str): Current password
            new_password (str): New password
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Verify old password
            if not user.check_password(old_password):
                return False, "Current password is incorrect."

            # Validate new password
            if old_password == new_password:
                return False, "New password must be different from current password."

            is_valid, message = AuthenticationService.validate_password_strength(new_password)
            if not is_valid:
                return False, message

            # Set new password
            user.set_password(new_password)
            user.save()
            
            logger.info(f"Password changed for user: {user.username}")
            return True, "Password changed successfully."

        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            return False, f"Error changing password: {str(e)}"

    @staticmethod
    def update_last_login(user, ip_address=None):
        """
        Update user's last login timestamp and IP.
        
        Args:
            user (User): The user object
            ip_address (str): User's IP address
        """
        try:
            user.last_login = now()
            user.save()
            
            if ip_address and hasattr(user, 'profile'):
                user.profile.last_login_ip = ip_address
                user.profile.last_login_time = now()
                user.profile.save()
                
        except Exception as e:
            logger.error(f"Error updating last login: {str(e)}")


class AuthorizationService:
    """
    Service for handling authorization and permission checks.
    """

    @staticmethod
    def is_admin(user):
        """Check if user is an admin."""
        return user.is_staff or user.is_superuser

    @staticmethod
    def is_analyst(user):
        """Check if user is a security analyst."""
        if not hasattr(user, 'profile'):
            return False
        return user.profile.is_analyst

    @staticmethod
    def has_permission(user, permission_name):
        """
        Check if user has specific permission.
        
        Args:
            user (User): The user object
            permission_name (str): Permission codename
            
        Returns:
            bool: True if user has permission
        """
        if user.is_superuser:
            return True
        return user.has_perm(permission_name)

    @staticmethod
    def can_access_project(user, project):
        """
        Check if user can access a specific project.
        
        Args:
            user (User): The user object
            project (Project): The project object
            
        Returns:
            bool: True if user can access project
        """
        # Admin can access all projects
        if AuthorizationService.is_admin(user):
            return True
        # Owner can access their projects
        if project.user == user:
            return True
        return False

    @staticmethod
    def can_modify_project(user, project):
        """
        Check if user can modify a specific project.
        
        Args:
            user (User): The user object
            project (Project): The project object
            
        Returns:
            bool: True if user can modify project
        """
        # Admin can modify all projects
        if AuthorizationService.is_admin(user):
            return True
        # Owner can modify their projects
        if project.user == user:
            return True
        return False

    @staticmethod
    def can_delete_project(user, project):
        """
        Check if user can delete a specific project.
        
        Args:
            user (User): The user object
            project (Project): The project object
            
        Returns:
            bool: True if user can delete project
        """
        # Admin can delete all projects
        if AuthorizationService.is_admin(user):
            return True
        # Owner can delete their projects
        if project.user == user:
            return True
        return False

    @staticmethod
    def can_access_analysis(user, analysis):
        """
        Check if user can access a specific analysis.
        
        Args:
            user (User): The user object
            analysis (ProjectAnalysis): The analysis object
            
        Returns:
            bool: True if user can access analysis
        """
        # Admin can access all analyses
        if AuthorizationService.is_admin(user):
            return True
        # User can access their own analyses
        if analysis.user == user:
            return True
        return False

    @staticmethod
    def can_delete_analysis(user, analysis):
        """
        Check if user can delete a specific analysis.
        
        Args:
            user (User): The user object
            analysis (ProjectAnalysis): The analysis object
            
        Returns:
            bool: True if user can delete analysis
        """
        # Admin can delete all analyses
        if AuthorizationService.is_admin(user):
            return True
        # User can delete their own analyses
        if analysis.user == user:
            return True
        return False
