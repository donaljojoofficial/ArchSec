from django import forms
from .models import Project

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

TESTING_CHOICES = [
    ('unit', 'Unit Testing'),
    ('integration', 'Integration Testing'),
    ('e2e', 'End-to-End Testing'),
    ('security_testing', 'Security Testing (SAST, DAST)'),
    ('performance_testing', 'Performance/Load Testing'),
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


class StructuredDataForm(forms.Form):
    # Requirements
    requirements = forms.MultipleChoiceField(choices=REQUIREMENTS_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    requirements_manual = forms.CharField(widget=forms.Textarea, required=False, label="Other Requirements")

    # Users
    users = forms.MultipleChoiceField(choices=USERS_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    users_manual = forms.CharField(widget=forms.Textarea, required=False, label="Other User Types")

    # Architecture
    architecture = forms.MultipleChoiceField(choices=ARCHITECTURE_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    architecture_manual = forms.CharField(widget=forms.Textarea, required=False, label="Other Architecture Patterns")

    # Technology
    technology = forms.MultipleChoiceField(choices=TECHNOLOGY_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    technology_manual = forms.CharField(widget=forms.Textarea, required=False, label="Other Technologies")

    # Security
    security = forms.MultipleChoiceField(choices=SECURITY_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    security_manual = forms.CharField(widget=forms.Textarea, required=False, label="Other Security Measures")

    # Performance
    performance = forms.MultipleChoiceField(choices=PERFORMANCE_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    performance_manual = forms.CharField(widget=forms.Textarea, required=False, label="Other Performance Strategies")

    # Database
    database = forms.MultipleChoiceField(choices=DATABASE_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    database_manual = forms.CharField(widget=forms.Textarea, required=False, label="Other Database Technologies")

    # Testing
    testing = forms.MultipleChoiceField(choices=TESTING_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    testing_manual = forms.CharField(widget=forms.Textarea, required=False, label="Other Testing Strategies")

    # Deployment
    deployment = forms.MultipleChoiceField(choices=DEPLOYMENT_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    deployment_manual = forms.CharField(widget=forms.Textarea, required=False, label="Other Deployment Methods")

    # Monitoring
    monitoring = forms.MultipleChoiceField(choices=MONITORING_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    monitoring_manual = forms.CharField(widget=forms.Textarea, required=False, label="Other Monitoring Solutions")

    # Compliance
    compliance = forms.MultipleChoiceField(choices=COMPLIANCE_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    compliance_manual = forms.CharField(widget=forms.Textarea, required=False, label="Other Compliance Requirements")

    # Privacy
    privacy = forms.MultipleChoiceField(choices=PRIVACY_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    privacy_manual = forms.CharField(widget=forms.Textarea, required=False, label="Other Privacy Measures")

    # Scalability
    scalability = forms.MultipleChoiceField(choices=SCALABILITY_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    scalability_manual = forms.CharField(widget=forms.Textarea, required=False, label="Other Scalability Strategies")

    # Infrastructure
    infrastructure = forms.MultipleChoiceField(choices=INFRASTRUCTURE_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    infrastructure_manual = forms.CharField(widget=forms.Textarea, required=False, label="Other Infrastructure")

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
            manual = self.cleaned_data.get(f"{section}_manual", "").strip()

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