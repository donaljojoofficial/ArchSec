# Quick Reference Guide - Authentication System

## URLs

| URL | Name | Purpose |
|-----|------|---------|
| `/login/` | login | User login |
| `/register/` | register | New user registration |
| `/logout/` | logout | Logout user |
| `/profile/` | profile | View user profile |
| `/profile/edit/` | edit_profile | Edit profile |
| `/profile/change-password/` | change_password | Change password |

## Views - Quick Examples

### Create a Protected View
```python
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def my_view(request):
    return render(request, 'my_template.html')
```

### Admin-Only View
```python
from core.decorators import admin_required

@admin_required
def admin_view(request):
    return render(request, 'admin_template.html')
```

### Project Owner View
```python
from core.decorators import project_owner_required

@project_owner_required
def project_action(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'action.html', {'project': project})
```

## Forms - Quick Reference

### Registration Form
```python
from core.forms import CustomUserCreationForm

if request.method == 'POST':
    form = CustomUserCreationForm(request.POST)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('dashboard')
```

### Profile Edit Form
```python
from core.forms import CustomUserChangeForm

if request.method == 'POST':
    form = CustomUserChangeForm(request.POST, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('profile')
```

### Password Change Form
```python
from core.forms import PasswordChangeForm

if request.method == 'POST':
    form = PasswordChangeForm(request.user, request.POST)
    if form.is_valid():
        AuthenticationService.change_password(
            request.user,
            form.cleaned_data['current_password'],
            form.cleaned_data['new_password']
        )
```

## Services - Quick Reference

### Create User
```python
from core.services.auth_service import AuthenticationService

user, error = AuthenticationService.create_user(
    username='john',
    email='john@example.com',
    password='SecurePass123'
)
if error:
    print(f"Error: {error}")
```

### Validate Password
```python
from core.services.auth_service import AuthenticationService

is_valid, message = AuthenticationService.validate_password_strength('MyPassword123')
print(message)  # "Password is strong."
```

### Check if Admin
```python
from core.services.auth_service import AuthorizationService

if AuthorizationService.is_admin(request.user):
    print("User is admin")
```

### Check Project Access
```python
from core.services.auth_service import AuthorizationService

can_access = AuthorizationService.can_access_project(request.user, project)
if not can_access:
    return HttpResponseForbidden()
```

## Templates - Common Patterns

### Check if User is Authenticated
```html
{% if user.is_authenticated %}
    Welcome, {{ user.username }}!
{% else %}
    Please login or register
{% endif %}
```

### Show Admin-Only Content
```html
{% if user.is_staff %}
    <a href="{% url 'admin:index' %}">Admin Panel</a>
{% endif %}
```

### User Menu Link
```html
<div class="user-menu">
    <a href="{% url 'profile' %}">My Profile</a>
    <a href="{% url 'change_password' %}">Change Password</a>
    <a href="{% url 'logout' %}">Logout</a>
</div>
```

## Models - Quick Reference

### UserProfile Fields
```python
user                  # ForeignKey to User
role                  # 'user', 'analyst', 'admin'
organization         # CharField
phone_number         # CharField
bio                  # TextField
avatar_url           # URLField
two_factor_enabled   # BooleanField (default: False)
is_verified          # BooleanField (default: False)
email_notifications  # BooleanField (default: True)
last_login_ip        # GenericIPAddressField
last_login_time      # DateTimeField
created_at           # DateTimeField (auto)
updated_at           # DateTimeField (auto)
```

### Access User Profile
```python
user = request.user
profile = user.profile  # OneToOne relationship

# Get profile properties
role = profile.role
is_admin = profile.is_admin  # property
is_analyst = profile.is_analyst  # property
```

## Decorators - All Available

| Decorator | Purpose | Example |
|-----------|---------|---------|
| `@login_required` | Requires authentication | `@login_required(login_url='login')` |
| `@admin_required` | Requires admin role | `@admin_required` |
| `@analyst_required` | Requires analyst or admin | `@analyst_required` |
| `@project_owner_required` | Requires project ownership | `@project_owner_required` |
| `@analysis_owner_required` | Requires analysis ownership | `@analysis_owner_required` |
| `@permission_required` | Requires specific permission | `@permission_required('core.change_project')` |

## Authentication Flow

### Registration Flow
```
1. User visits /register/
2. Fills out form with username, email, password
3. Submit → CustomUserCreationForm validates
4. If valid → User created, profile auto-created
5. Auto-login → Redirect to dashboard
```

### Login Flow
```
1. User visits /login/
2. Enters username/email and password
3. Django authenticates credentials
4. If valid → Session created, redirect to dashboard
5. If invalid → Show error message
```

### Project Access Flow
```
1. User visits /project/{id}/
2. @project_owner_required checks ownership
3. get_object_or_404(Project, id=id, user=request.user)
4. If owner → Show content
5. If not owner → Redirect to dashboard with error
```

## Common Errors & Solutions

### 401 Unauthorized
- Cause: User not authenticated
- Solution: Add @login_required decorator

### 403 Forbidden
- Cause: User not authorized
- Solution: Check user role/permissions

### 404 Not Found
- Cause: Project doesn't exist or user doesn't own it
- Solution: Verify project ID and ownership

### Password Validation Failed
- Cause: Password doesn't meet requirements
- Solution: Password must be 8+ chars, have uppercase and digit

### Duplicate Email
- Cause: Email already registered
- Solution: Use different email or reset password

## Admin Tasks

### Create User via Admin
1. Go to /admin/auth/user/add/
2. Enter username and password
3. Save and continue editing → Add more fields
4. Change role in UserProfile inline

### Reset User Password
1. Go to /admin/auth/user/
2. Click on user
3. Click "this form" link next to password
4. Enter new password

### View Login History
1. Go to /admin/core/userprofile/
2. View last_login_ip and last_login_time

### Manage Project Access
1. Go to /admin/core/project/
2. Check project.user for ownership
3. Filter by user or platform

## Security Tips

1. **Always use @login_required**
   ```python
   @login_required(login_url='login')
   def my_view(request): ...
   ```

2. **Verify ownership in views**
   ```python
   project = get_object_or_404(Project, id=id, user=request.user)
   ```

3. **Use get_object_or_404**
   ```python
   # Good - returns 404 if not found
   obj = get_object_or_404(Model, id=id, user=request.user)
   
   # Bad - could expose data
   obj = Model.objects.get(id=id)
   ```

4. **Log authorization failures**
   ```python
   if not AuthorizationService.can_access_project(request.user, project):
       logger.warning(f"Unauthorized access: {request.user.username}")
   ```

5. **Use messages for user feedback**
   ```python
   messages.error(request, 'You do not have permission.')
   ```

## Testing

### Test Authentication
```python
from django.test import TestCase, Client
from django.contrib.auth.models import User

class AuthTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'testuser', 'test@example.com', 'pass123'
        )
    
    def test_login(self):
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'pass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
```

### Test Authorization
```python
def test_project_access(self):
    project = Project.objects.create(
        user=self.user,
        name='Test Project'
    )
    
    response = self.client.get(f'/project/{project.id}/')
    self.assertEqual(response.status_code, 200)
```

## Useful Commands

```bash
# Create superuser
python manage.py createsuperuser

# Create regular user
python manage.py shell
>>> from core.services.auth_service import AuthenticationService
>>> AuthenticationService.create_user('user', 'email@test.com', 'Pass123')

# Check if user is staff
python manage.py shell
>>> user = User.objects.get(username='test')
>>> user.is_staff

# Reset user password
python manage.py changepassword username

# View database records
python manage.py dbshell
> SELECT * FROM auth_user;

# Run tests
python manage.py test core

# Check project ownership
python manage.py shell
>>> from core.models import Project
>>> p = Project.objects.get(id=1)
>>> p.user.username
```

## Documentation Files

- **Full Auth Documentation**: `AUTH_SYSTEM.md`
- **Implementation Details**: `IMPLEMENTATION_SUMMARY.md`
- **This Quick Reference**: `QUICK_REFERENCE.md`

---

For detailed information, see `AUTH_SYSTEM.md`
