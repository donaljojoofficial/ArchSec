from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
import re
from .models import Project


CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
SAFE_TEXT_LIMITS = {
    "name": 120,
    "description": 3000,
    "tech_stack": 500,
    "scale": 255,
    "manual": 2000,
}


def clean_user_text(value, max_length=2000):
    """
    Normalize stored free-text input so it is safer to render and send to AI.
    This does not make text "trusted"; templates should still auto-escape it.
    """
    if value is None:
        return ""

    value = str(value).replace("\r\n", "\n").replace("\r", "\n")
    if len(value) > max_length * 3:
        raise ValidationError(f"Keep this field under {max_length} characters.")
    value = CONTROL_CHAR_RE.sub("", value)
    value = strip_tags(value)
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{4,}", "\n\n\n", value).strip()

    if len(value) > max_length:
        raise ValidationError(f"Keep this field under {max_length} characters.")

    return value


# ========================
# Authentication Forms
# ========================

class CustomUserCreationForm(UserCreationForm):
    """
    Extended user creation form with email and additional validation.
    """
    email = forms.EmailField(
        required=True,
        help_text='Required. Enter a valid email address.',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        help_text='Optional.',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        help_text='Optional.',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add styling to form fields
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Enter a strong password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm password'
        self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'

    def clean_email(self):
        """Check if email already exists."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email address is already in use.')
        return email

    def clean_username(self):
        """Check if username already exists."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('This username is already taken.')
        return username

    def clean(self):
        """Additional validation."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not match.')

        # Check password strength
        if password1:
            if len(password1) < 8:
                raise ValidationError('Password must be at least 8 characters long.')
            if password1.isdigit():
                raise ValidationError('Password cannot be entirely numeric.')

        return cleaned_data


class CustomUserChangeForm(UserChangeForm):
    """
    Extended user change form for updating profile.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'
        # Hide password field
        if 'password' in self.fields:
            del self.fields['password']


class PasswordChangeForm(forms.Form):
    """
    Form for users to change their password.
    """
    current_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your current password'
        })
    )
    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter a new password'
        })
    )
    new_password_confirm = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your new password'
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        new_password_confirm = cleaned_data.get('new_password_confirm')

        if new_password and new_password_confirm:
            if new_password != new_password_confirm:
                raise ValidationError('Passwords do not match.')

            if len(new_password) < 8:
                raise ValidationError('Password must be at least 8 characters long.')

        return cleaned_data


# ========================
# Project Forms (Existing)
# ========================

# (Existing ProjectForm kept for backward compatibility if needed)
class OldProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'name',
            'description',
            'platform',
            'tech_stack',
            'scale',
            'budget',
            'risk_level',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["description"]}),
            'name': forms.TextInput(attrs={'maxlength': SAFE_TEXT_LIMITS["name"]}),
            'tech_stack': forms.TextInput(attrs={'maxlength': SAFE_TEXT_LIMITS["tech_stack"]}),
            'scale': forms.TextInput(attrs={'maxlength': SAFE_TEXT_LIMITS["scale"]}),
        }

    def clean_name(self):
        return clean_user_text(self.cleaned_data.get("name"), SAFE_TEXT_LIMITS["name"])

    def clean_description(self):
        return clean_user_text(self.cleaned_data.get("description"), SAFE_TEXT_LIMITS["description"])

    def clean_tech_stack(self):
        return clean_user_text(self.cleaned_data.get("tech_stack"), SAFE_TEXT_LIMITS["tech_stack"])

    def clean_scale(self):
        return clean_user_text(self.cleaned_data.get("scale"), SAFE_TEXT_LIMITS["scale"])

# --- Constants for Structured Data ---

REQUIREMENTS_CHOICES = [
    ('functional', 'Functional Requirements'),
    ('non_functional', 'Non-Functional Requirements'),
    ('business', 'Business Rules'),
    ('user_stories', 'User Stories'),
]

USERS_CHOICES = [
    ('public', 'Public/Anonymous Users'),
    ('authenticated', 'Authenticated Users'),
    ('admin', 'Administrators/Superusers'),
    ('third_party', 'Third-Party Integrations'),
]

ARCHITECTURE_CHOICES = [
    ('monolith', 'Monolithic'),
    ('microservices', 'Microservices'),
    ('serverless', 'Serverless'),
    ('event_driven', 'Event-Driven'),
    ('layered', 'Layered (N-Tier)'),
]

TECHNOLOGY_CHOICES = [
    ('python', 'Python (Django, Flask)'),
    ('javascript', 'JavaScript (Node.js, React, Vue)'),
    ('java', 'Java (Spring, Jakarta EE)'),
    ('csharp', 'C# (.NET)'),
    ('php', 'PHP (Laravel, Symfony)'),
    ('ruby', 'Ruby on Rails'),
]

BACKEND_CHOICES = [
    ('php_legacy', 'Legacy PHP application'),
    ('wordpress', 'WordPress or plugin-heavy CMS backend'),
    ('dotnet_framework', '.NET Framework / WebForms / MVC'),
    ('java_legacy', 'Legacy Java / Spring / JSP'),
    ('python_legacy', 'Legacy Python / Django / Flask'),
    ('node_legacy', 'Older Node.js / Express services'),
    ('serverless', 'Serverless functions'),
    ('unknown_backend', 'Unknown or poorly documented backend'),
]

FRONTEND_CHOICES = [
    ('server_rendered', 'Server-rendered templates'),
    ('jquery', 'jQuery or imperative JavaScript'),
    ('legacy_spa', 'Older SPA framework/version'),
    ('modern_spa', 'React, Vue, Angular, or Svelte'),
    ('static_site', 'Static site'),
    ('mobile_web', 'Mobile-oriented web frontend'),
]

CMS_FRAMEWORK_CHOICES = [
    ('wordpress', 'WordPress'),
    ('drupal', 'Drupal'),
    ('joomla', 'Joomla'),
    ('shopify', 'Shopify'),
    ('magento', 'Magento / Adobe Commerce'),
    ('custom_framework', 'Custom framework'),
    ('no_cms', 'No CMS'),
    ('unknown_cms', 'Unknown CMS/framework'),
]

SECURITY_CHOICES = [
    ('authentication', 'Authentication (OAuth, JWT, SSO)'),
    ('authorization', 'Authorization (RBAC, ABAC)'),
    ('encryption', 'Data Encryption (At-rest, In-transit)'),
    ('logging_monitoring', 'Security Logging & Monitoring'),
    ('ids_ips', 'Intrusion Detection/Prevention System (IDS/IPS)'),
    ('waf', 'Web Application Firewall (WAF)'),
]

PERFORMANCE_CHOICES = [
    ('caching', 'Caching (CDN, In-memory)'),
    ('load_balancing', 'Load Balancing'),
    ('async_processing', 'Asynchronous Processing (Celery, RabbitMQ)'),
    ('database_optimization', 'Database Query Optimization'),
]

DATABASE_CHOICES = [
    ('sql', 'SQL (PostgreSQL, MySQL)'),
    ('nosql', 'NoSQL (MongoDB, Cassandra)'),
    ('newsql', 'NewSQL (CockroachDB, TiDB)'),
    ('graph', 'Graph (Neo4j)'),
]

HOSTING_CHOICES = [
    ('shared_hosting', 'Shared hosting'),
    ('vps', 'VPS / manually managed VM'),
    ('on_premise', 'On-premise servers'),
    ('cloud_vm', 'Cloud VM'),
    ('paas', 'Platform as a Service'),
    ('containers', 'Containers / Kubernetes'),
    ('static_cdn', 'Static hosting / CDN'),
    ('unknown_hosting', 'Unknown hosting'),
]

RUNTIME_AGE_CHOICES = [
    ('current', 'Current or actively supported versions'),
    ('slightly_old', 'One to two major versions behind'),
    ('end_of_life', 'End-of-life runtime or framework'),
    ('unsupported_os', 'Unsupported operating system'),
    ('unknown_versions', 'Versions are unknown or undocumented'),
]

TESTING_CHOICES = [
    ('unit', 'Unit Testing'),
    ('integration', 'Integration Testing'),
    ('e2e', 'End-to-End Testing'),
    ('security_testing', 'Security Testing (SAST, DAST)'),
    ('performance_testing', 'Performance/Load Testing'),
]

TESTING_PROCESS_CHOICES = [
    ('manual_only', 'Manual QA only'),
    ('ad_hoc_testing', 'Ad hoc developer testing'),
    ('partial_automation', 'Partial automated tests'),
    ('ci_tests', 'Tests run in CI'),
    ('coverage_tracking', 'Coverage is tracked'),
    ('release_gates', 'Automated release gates'),
]

SECURITY_TESTING_CHOICES = [
    ('none', 'No formal security testing'),
    ('sast', 'Static analysis / SAST'),
    ('dast', 'Dynamic testing / DAST'),
    ('sca', 'Dependency scanning / SCA'),
    ('secrets_scanning', 'Secrets scanning'),
    ('container_scanning', 'Container image scanning'),
    ('pentest', 'Periodic penetration testing'),
]

DEPLOYMENT_CHOICES = [
    ('manual', 'Manual Deployment'),
    ('ci_cd', 'CI/CD Pipelines'),
    ('containerization', 'Containerization (Docker, Kubernetes)'),
    ('iaac', 'Infrastructure as Code (Terraform, Ansible)'),
]

MONITORING_CHOICES = [
    ('logging', 'Centralized Logging (ELK, Splunk)'),
    ('metrics', 'Metrics & Visualization (Prometheus, Grafana)'),
    ('tracing', 'Distributed Tracing (Jaeger, Zipkin)'),
    ('apm', 'Application Performance Monitoring (APM)'),
]

OBSERVABILITY_CHOICES = [
    ('basic_logs', 'Basic application/server logs'),
    ('centralized_logs', 'Centralized logs'),
    ('metrics_dashboards', 'Metrics dashboards'),
    ('alerting', 'Alerting/on-call workflow'),
    ('tracing', 'Distributed tracing'),
    ('error_tracking', 'Error tracking'),
    ('uptime_monitoring', 'Uptime monitoring'),
]

BACKUP_INCIDENT_CHOICES = [
    ('manual_backups', 'Manual backups'),
    ('automated_backups', 'Automated backups'),
    ('restore_tests', 'Restore tests are performed'),
    ('incident_runbook', 'Incident response runbook'),
    ('dr_plan', 'Disaster recovery plan'),
    ('no_known_backups', 'No known backup process'),
]

COMPLIANCE_CHOICES = [
    ('gdpr', 'GDPR'),
    ('pci_dss', 'PCI-DSS'),
    ('hipaa', 'HIPAA'),
    ('iso_27001', 'ISO 27001'),
    ('soc_2', 'SOC 2'),
]

PRIVACY_CHOICES = [
    ('pii_handling', 'PII Data Handling & Masking'),
    ('consent_management', 'User Consent Management'),
    ('data_anonymization', 'Data Anonymization'),
]

SCALABILITY_CHOICES = [
    ('vertical', 'Vertical Scaling'),
    ('horizontal', 'Horizontal Scaling (Auto-scaling)'),
    ('database_scaling', 'Database Scaling (Read Replicas, Sharding)'),
]

INFRASTRUCTURE_CHOICES = [
    ('on_premise', 'On-Premise'),
    ('cloud_aws', 'Cloud (AWS)'),
    ('cloud_gcp', 'Cloud (GCP)'),
    ('cloud_azure', 'Cloud (Azure)'),
    ('hybrid', 'Hybrid Cloud'),
]

LEGACY_CHOICES = [
    ('old_runtime', 'Old runtime or framework version'),
    ('manual_deployments', 'Manual or FTP-based deployments'),
    ('limited_documentation', 'Limited technical documentation'),
    ('monolithic_codebase', 'Large monolithic codebase'),
    ('unsupported_dependencies', 'Unsupported or unpatched dependencies'),
    ('no_environment_parity', 'Development/staging/production are inconsistent'),
]

AI_READINESS_CHOICES = [
    ('no_ai_usage', 'No current AI integration'),
    ('customer_support_ai', 'Customer support assistant opportunity'),
    ('internal_knowledge_ai', 'Internal knowledge/search assistant opportunity'),
    ('analytics_ai', 'AI-assisted reporting or analytics opportunity'),
    ('workflow_automation', 'Workflow automation opportunity'),
    ('privacy_constraints', 'Sensitive data or privacy constraints'),
]

MIGRATION_CONSTRAINT_CHOICES = [
    ('limited_budget', 'Limited budget'),
    ('tight_timeline', 'Tight timeline'),
    ('low_downtime_tolerance', 'Low downtime tolerance'),
    ('small_team', 'Small team'),
    ('limited_modern_stack_experience', 'Limited modern stack experience'),
    ('compliance_requirements', 'Compliance requirements'),
    ('legacy_vendor_lock_in', 'Legacy vendor lock-in'),
    ('data_migration_complexity', 'Data migration complexity'),
]


class StructuredDataForm(forms.Form):
    # Requirements
    requirements = forms.MultipleChoiceField(choices=REQUIREMENTS_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    requirements_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Other Requirements")

    # Users
    users = forms.MultipleChoiceField(choices=USERS_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    users_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Other User Types")

    # Architecture
    architecture = forms.MultipleChoiceField(choices=ARCHITECTURE_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    architecture_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Other Architecture Patterns")

    # Technology
    technology = forms.MultipleChoiceField(choices=TECHNOLOGY_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    technology_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Other Technologies")

    # Current stack detail
    current_backend = forms.MultipleChoiceField(choices=BACKEND_CHOICES, widget=forms.CheckboxSelectMultiple, required=False, label="Current Backend")
    current_backend_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Backend Version Notes")

    current_frontend = forms.MultipleChoiceField(choices=FRONTEND_CHOICES, widget=forms.CheckboxSelectMultiple, required=False, label="Current Frontend")
    current_frontend_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Frontend Version Notes")

    cms_framework = forms.MultipleChoiceField(choices=CMS_FRAMEWORK_CHOICES, widget=forms.CheckboxSelectMultiple, required=False, label="CMS / Framework")
    cms_framework_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="CMS / Framework Notes")

    runtime_age = forms.MultipleChoiceField(choices=RUNTIME_AGE_CHOICES, widget=forms.CheckboxSelectMultiple, required=False, label="Runtime / Framework Age")
    runtime_age_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Version Details")

    # Security
    security = forms.MultipleChoiceField(choices=SECURITY_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    security_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Other Security Measures")

    # Performance
    performance = forms.MultipleChoiceField(choices=PERFORMANCE_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    performance_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Other Performance Strategies")

    # Database
    database = forms.MultipleChoiceField(choices=DATABASE_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    database_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Other Database Technologies")

    # Hosting
    hosting = forms.MultipleChoiceField(choices=HOSTING_CHOICES, widget=forms.CheckboxSelectMultiple, required=False, label="Hosting Environment")
    hosting_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Hosting Notes")

    # Testing
    testing = forms.MultipleChoiceField(choices=TESTING_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    testing_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Other Testing Strategies")

    testing_process = forms.MultipleChoiceField(choices=TESTING_PROCESS_CHOICES, widget=forms.CheckboxSelectMultiple, required=False, label="Current Testing Process")
    testing_process_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Testing Coverage Notes")

    security_testing_process = forms.MultipleChoiceField(choices=SECURITY_TESTING_CHOICES, widget=forms.CheckboxSelectMultiple, required=False, label="Security Testing Process")
    security_testing_process_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Security Testing Notes")

    # Deployment
    deployment = forms.MultipleChoiceField(choices=DEPLOYMENT_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    deployment_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Other Deployment Methods")

    # Monitoring
    monitoring = forms.MultipleChoiceField(choices=MONITORING_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    monitoring_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Other Monitoring Solutions")

    observability_operations = forms.MultipleChoiceField(choices=OBSERVABILITY_CHOICES, widget=forms.CheckboxSelectMultiple, required=False, label="Observability And Operations")
    observability_operations_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Logging, Alerting, Or Incident Notes")

    backups_incident_response = forms.MultipleChoiceField(choices=BACKUP_INCIDENT_CHOICES, widget=forms.CheckboxSelectMultiple, required=False, label="Backups And Incident Response")
    backups_incident_response_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Backup Or Recovery Notes")

    # Compliance
    compliance = forms.MultipleChoiceField(choices=COMPLIANCE_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    compliance_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Other Compliance Requirements")

    # Privacy
    privacy = forms.MultipleChoiceField(choices=PRIVACY_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    privacy_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Other Privacy Measures")

    # Scalability
    scalability = forms.MultipleChoiceField(choices=SCALABILITY_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    scalability_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Other Scalability Strategies")

    # Infrastructure
    infrastructure = forms.MultipleChoiceField(choices=INFRASTRUCTURE_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    infrastructure_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Other Infrastructure")

    # Legacy Modernization
    legacy_constraints = forms.MultipleChoiceField(choices=LEGACY_CHOICES, widget=forms.CheckboxSelectMultiple, required=False, label="Legacy Constraints")
    legacy_constraints_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Other Legacy Constraints")

    # AI Readiness
    ai_readiness = forms.MultipleChoiceField(choices=AI_READINESS_CHOICES, widget=forms.CheckboxSelectMultiple, required=False, label="AI Readiness")
    ai_readiness_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Other AI Opportunities")

    # Migration Constraints
    migration_constraints = forms.MultipleChoiceField(choices=MIGRATION_CONSTRAINT_CHOICES, widget=forms.CheckboxSelectMultiple, required=False, label="Migration Constraints")
    migration_constraints_manual = forms.CharField(widget=forms.Textarea(attrs={'maxlength': SAFE_TEXT_LIMITS["manual"]}), required=False, label="Timeline, Downtime, Team, Or Compliance Notes")

    def get_structured_data(self):
        """
        Merges the selected choices and manual inputs into a dictionary
        structured for the Project model's JSONField.
        """
        if not self.is_valid():
            return {}

        data = {}
        for section, _ in self.fields.items():
            if '_manual' in section:
                continue

            selected = self.cleaned_data.get(section, [])
            manual = clean_user_text(
                self.cleaned_data.get(f"{section}_manual", ""),
                SAFE_TEXT_LIMITS["manual"],
            )

            section_data = {}
            if selected:
                section_data['options'] = selected
            if manual:
                section_data['manual_input'] = manual

            if section_data:
                data[section] = section_data
        return data

class ProjectForm(OldProjectForm, StructuredDataForm):
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        StructuredDataForm.__init__(self, *args, **kwargs)
        self.fields["budget"].required = False
        self.fields["budget"].label = "Known modernization budget"
        self.fields["budget"].help_text = "Optional. Leave blank and ArchSec will estimate budget ranges from the assessment."
        self.fields["risk_level"].required = False
        self.fields["risk_level"].label = "Known business risk"
        self.fields["risk_level"].help_text = "Optional. Leave blank and ArchSec will estimate modernization risk."

    def clean(self):
        cleaned_data = super().clean()
        for field_name in self.fields:
            if field_name.endswith("_manual"):
                try:
                    cleaned_data[field_name] = clean_user_text(
                        cleaned_data.get(field_name, ""),
                        SAFE_TEXT_LIMITS["manual"],
                    )
                except ValidationError as error:
                    self.add_error(field_name, error)
        return cleaned_data
