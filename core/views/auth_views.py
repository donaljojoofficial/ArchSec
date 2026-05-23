from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import logging

from core.forms import CustomUserCreationForm, CustomUserChangeForm, PasswordChangeForm
from core.models import UserProfile
from core.services.auth_service import AuthenticationService, AuthorizationService

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def register_view(request):
    """
    User registration view with validation.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                
                # Get user's IP address for logging
                ip_address = get_client_ip(request)
                AuthenticationService.update_last_login(user, ip_address)
                
                # Log in user immediately after registration
                login(request, user)
                messages.success(request, f'Welcome {user.username}! Your account has been created successfully.')
                logger.info(f"New user registered: {user.username}")
                return redirect('dashboard')
            except Exception as e:
                logger.error(f"Error during registration: {str(e)}")
                messages.error(request, f'An error occurred during registration: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


def logout_view(request):
    """
    User logout view.
    Clears session and redirects to login page.
    Supports both GET and POST requests (POST preferred).
    """
    # Get username before logout
    username = request.user.username if request.user.is_authenticated else 'Anonymous'
    
    # Perform logout
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        logger.info(f"User logged out: {username}")
    else:
        # User already logged out or never logged in
        messages.info(request, 'You were already logged out.')
        logger.debug(f"Logout requested by unauthenticated user")
    
    return redirect('home')


@login_required(login_url='login')
def profile_view(request):
    """
    User profile view showing user information and settings.
    """
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    context = {
        'user': request.user,
        'profile': profile,
    }
    return render(request, 'registration/profile.html', context)


@require_http_methods(["GET", "POST"])
@login_required(login_url='login')
def edit_profile_view(request):
    """
    Edit user profile view.
    """
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        
        if form.is_valid():
            try:
                user = form.save()
                
                # Update profile fields if provided
                if request.POST.get('organization'):
                    profile.organization = request.POST.get('organization')
                if request.POST.get('phone_number'):
                    profile.phone_number = request.POST.get('phone_number')
                if request.POST.get('bio'):
                    profile.bio = request.POST.get('bio')
                profile.save()
                
                messages.success(request, 'Your profile has been updated successfully.')
                logger.info(f"Profile updated for user: {user.username}")
                return redirect('profile')
            except Exception as e:
                logger.error(f"Error updating profile: {str(e)}")
                messages.error(request, f'An error occurred while updating your profile: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserChangeForm(instance=request.user)

    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'registration/edit_profile.html', context)


@require_http_methods(["GET", "POST"])
@login_required(login_url='login')
def change_password_view(request):
    """
    Change password view with current password verification.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            try:
                old_password = form.cleaned_data['current_password']
                new_password = form.cleaned_data['new_password']
                
                success, message = AuthenticationService.change_password(
                    request.user, 
                    old_password, 
                    new_password
                )
                
                if success:
                    # Update session to avoid logout
                    update_session_auth_hash(request, request.user)
                    messages.success(request, message)
                    logger.info(f"Password changed for user: {request.user.username}")
                    return redirect('profile')
                else:
                    messages.error(request, message)
            except Exception as e:
                logger.error(f"Error changing password: {str(e)}")
                messages.error(request, f'An error occurred: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = PasswordChangeForm(request.user)

    context = {
        'form': form,
    }
    return render(request, 'registration/change_password.html', context)


def get_client_ip(request):
    """
    Get client IP address from request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
