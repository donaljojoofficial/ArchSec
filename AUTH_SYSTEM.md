# Authentication & Authorization Documentation

## Overview

PlaniX now has a robust, production-ready authentication and authorization system. This document explains the features, architecture, and usage of the authentication system.

## Features

### 1. **User Registration**
- Self-service user registration with email validation
- Strong password requirements:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one digit (0-9)
  - Cannot be entirely numeric
- Duplicate username and email prevention
- Automatic user profile creation

### 2. **User Authentication**
- Django's built-in authentication system
- Session-based authentication
- Secure cookie settings (HTTPONLY, SECURE, SAMESITE)
- Session timeout after 30 minutes of inactivity
- IP address and login time tracking

### 3. **User Profiles**
- Extended user information storage
- User roles:
  - **Regular User**: Standard user with project management capabilities
  - **Analyst**: Security analyst with additional analysis features
  - **Administrator**: Full system access
- Optional profile fields:
  - Bio
  - Organization
  - Phone number
  - Avatar URL
  - Two-factor authentication status (disabled by default)

### 4. **Access Control**
- Project-level access control
- User ownership verification
- Admin override capabilities
- Permission decorators for fine-grained control

### 5. **Password Management**
- Secure password change functionality
- Current password verification required
- New password must be different from old password
- Same validation rules as registration

### 6. **User Account Management**
- Editable profile information
- View login history and activity
- Account status verification
- Email address management

## Architecture

### Models

#### UserProfile
```python
- Extends Django's User model with OneToOne relationship
- Fields:
  - role: User's role (user/analyst/admin)
  - organization: User's organization
  - phone_number: Contact phone
  - bio: User biography
  - avatar_url: Profile image URL
  - two_factor_enabled: 2FA status
  - is_verified: Email verification status
  - email_notifications: Notification preference
  - last_login_ip: Last login IP address
  - last_login_time: Last login timestamp
  - created_at, updated_at: Metadata
```

### Views

#### Authentication Views (`core/views/auth_views.py`)
- `register_view`: User registration
- `logout_view`: Secure logout
- `profile_view`: View user profile
- `edit_profile_view`: Edit profile information
- `change_password_view`: Change password

#### Project Views with Permission Checks
- `create_project`: Create new project
- `generate_analysis`: Generate security analysis (owner only)
- `view_analysis`: View analysis (owner/admin only)
- `history_analysis`: View project analysis history (owner only)
- `download_analysis_pdf`: Download PDF (owner/admin only)
- `export_analysis_md/txt`: Export analysis (owner/admin only)

### Services

#### AuthenticationService (`core/services/auth_service.py`)
Provides authentication utilities:
- `validate_password_strength()`: Check password requirements
- `create_user()`: Create user with validation
- `change_password()`: Update password securely
- `update_last_login()`: Track user login activity

#### AuthorizationService (`core/services/auth_service.py`)
Provides authorization utilities:
- `is_admin()`: Check if user is admin
- `is_analyst()`: Check if user is analyst
- `has_permission()`: Check specific permission
- `can_access_project()`: Project access check
- `can_modify_project()`: Project modification check
- `can_access_analysis()`: Analysis access check
- `can_delete_analysis()`: Analysis deletion check

### Decorators (`core/decorators.py`)

#### `@admin_required`
Restricts view to administrators only.
```python
from core.decorators import admin_required

@admin_required
def admin_only_view(request):
    pass
```

#### `@analyst_required`
Restricts view to analysts and administrators.
```python
from core.decorators import analyst_required

@analyst_required
def analyst_view(request):
    pass
```

#### `@project_owner_required`
Restricts view to project owner or admin.
```python
from core.decorators import project_owner_required

@project_owner_required
def project_action(request, project_id):
    pass
```

#### `@analysis_owner_required`
Restricts view to analysis owner or admin.
```python
from core.decorators import analysis_owner_required

@analysis_owner_required
def analysis_action(request, analysis_id):
    pass
```

#### `@permission_required(permission_codename)`
Checks for specific Django permission.
```python
from core.decorators import permission_required

@permission_required('core.change_project')
def modify_view(request):
    pass
```

## Security Configuration

### Settings (`planix/settings.py`)

#### Session Security
```python
SESSION_COOKIE_AGE = 1800  # 30 minutes
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = True  # HTTPS only (production)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
```

#### CSRF Protection
```python
CSRF_COOKIE_SECURE = True  # HTTPS only (production)
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
```

#### Security Headers
```python
SECURE_HSTS_SECONDS = 31536000  # 1 year (production)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_SSL_REDIRECT = True  # HTTPS only (production)
SECURE_BROWSER_XSS_FILTER = True
```

#### Password Validation
Django's built-in password validators:
- UserAttributeSimilarityValidator
- MinimumLengthValidator
- CommonPasswordValidator
- NumericPasswordValidator

## Forms

### CustomUserCreationForm
Enhanced registration form with:
- Email field (required, unique)
- First name and last name (optional)
- Password strength validation
- Duplicate prevention

### CustomUserChangeForm
Profile editing form with:
- Email field (editable)
- First/Last name
- Password field removed

### PasswordChangeForm
Password change form with:
- Current password verification
- New password confirmation
- Validation rules enforcement

## Templates

### Authentication Templates
- `registration/login.html` - Login page
- `registration/register.html` - Registration page
- `registration/profile.html` - User profile view
- `registration/edit_profile.html` - Profile editor
- `registration/change_password.html` - Password change

### Navigation Updates
- User dropdown menu in navbar
- Profile and settings links
- Admin panel access for staff
- Register/Login buttons for anonymous users

## URL Routing

```python
# Authentication URLs
path('login/', auth_views.LoginView.as_view(), name='login')
path('register/', register_view, name='register')
path('logout/', logout_view, name='logout')
path('profile/', profile_view, name='profile')
path('profile/edit/', edit_profile_view, name='edit_profile')
path('profile/change-password/', change_password_view, name='change_password')
```

## Usage Examples

### Protecting a View
```python
from django.contrib.auth.decorators import login_required
from core.decorators import admin_required

@login_required(login_url='login')
@admin_required
def admin_dashboard(request):
    # Only authenticated admins can access
    return render(request, 'admin_dashboard.html')
```

### Checking Permissions in View
```python
from core.services.auth_service import AuthorizationService

def project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if not AuthorizationService.can_access_project(request.user, project):
        return HttpResponseForbidden("Access Denied")
    
    return render(request, 'project.html', {'project': project})
```

### Creating a User Programmatically
```python
from core.services.auth_service import AuthenticationService

user, error = AuthenticationService.create_user(
    username='newuser',
    email='user@example.com',
    password='SecurePass123',
    first_name='John',
    last_name='Doe'
)

if error:
    print(f"Error: {error}")
else:
    print(f"User created: {user.username}")
```

### Changing Password
```python
from core.services.auth_service import AuthenticationService

success, message = AuthenticationService.change_password(
    user=request.user,
    old_password='CurrentPass123',
    new_password='NewPass456'
)

if success:
    print("Password changed successfully")
else:
    print(f"Error: {message}")
```

## Admin Interface

The Django admin interface has been enhanced with:

### User Management
- View all users with roles
- Filter by staff status, activity, role
- Manage user profiles inline
- View last login information

### User Profile Management
- Manage user roles and settings
- View and update organization, phone, bio
- Track login activity
- Enable/disable features (2FA, email notifications)

### Project Management
- View all projects with ownership
- Filter by platform, risk level, date
- Quick access to project data

### Analysis Management
- View analysis with metadata
- Filter by risk category, score, user
- Track analysis history

### Notifications
- View all user notifications
- Filter by read status and date
- Delete notifications

## Security Best Practices

1. **Password Requirements**
   - Enforce strong passwords in all forms
   - Require minimum 8 characters
   - Require mixed case and numbers

2. **Session Management**
   - Set appropriate session timeout (30 minutes default)
   - Use secure, HTTP-only cookies
   - Enable CSRF protection

3. **Data Protection**
   - Verify ownership before allowing access
   - Use get_object_or_404 for permission checks
   - Log unauthorized access attempts

4. **Admin Access**
   - Use Django admin only for staff
   - Require staff status for sensitive operations
   - Enable audit logging for admin changes

5. **Communication**
   - Use HTTPS in production
   - Enable HSTS headers
   - Secure cookie transmission

## Testing Authentication

### Create Test User
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.create_user('testuser', 'test@example.com', 'TestPass123')
>>> user.is_staff = True
>>> user.save()
```

### Test Login
```bash
python manage.py shell
>>> from django.contrib.auth import authenticate
>>> user = authenticate(username='testuser', password='TestPass123')
>>> print(user)  # Should print the user object
```

### Check Permissions
```bash
python manage.py shell
>>> from core.services.auth_service import AuthorizationService
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='testuser')
>>> print(AuthorizationService.is_admin(user))  # True if staff
```

## Migration Guide

### From Old Authentication System

If you're upgrading from the previous system:

1. **Run migrations**: `python manage.py migrate`
2. **Create user profiles**: Profiles are auto-created via signal
3. **Set user roles**: Edit users in admin to assign roles
4. **Update permissions**: Configure Django permissions as needed
5. **Test access**: Verify all views work with new system

## Troubleshooting

### User Cannot Login
- Verify user account exists: `User.objects.filter(username='...').exists()`
- Check user is active: `user.is_active`
- Reset password if needed

### Permission Denied Errors
- Check user role: `user.profile.role`
- Verify project ownership: `project.user == request.user`
- Check is_staff for admin views

### Session Timeout Issues
- Check SESSION_COOKIE_AGE setting
- Verify middleware order
- Check browser cookie settings

## Future Enhancements

1. Two-factor authentication (2FA)
2. Social authentication (OAuth)
3. API token authentication
4. Advanced role-based access control (RBAC)
5. Audit logging system
6. Email verification
7. Password reset functionality

## Support

For issues or questions about authentication:
1. Check Django docs: https://docs.djangoproject.com/en/stable/topics/auth/
2. Review code comments in `core/services/auth_service.py`
3. Check decorator implementations in `core/decorators.py`
