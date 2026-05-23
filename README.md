# ArchSec - AI Modernization Advisor

ArchSec is an AI-assisted modernization platform for teams running old websites, legacy applications, dated infrastructure, or traditional development and security workflows.

Instead of producing one generic report, ArchSec analyzes the user's current system and breaks the result into clear modernization issues. Each issue includes the current problem, business/technical impact, recommended modern solution, migration requirements, estimated cost, implementation effort, risks, and supporting diagrams or flow charts where helpful.

## Product Vision

Many organizations still depend on older stacks, manual deployment, outdated testing practices, limited security automation, and systems that were built before AI-enabled workflows became practical. ArchSec helps those teams understand what to modernize, why it matters, what it will cost, and how to migrate without losing control of the existing system.

The platform is intended for:

- Small businesses with aging websites or admin panels.
- Teams using traditional deployment, manual QA, or ad hoc security testing.
- Organizations that want to add AI capabilities to existing systems.
- Developers and consultants preparing modernization proposals.
- Security engineers evaluating legacy application risk.

## Core Outcome

ArchSec converts a legacy system profile into an actionable modernization roadmap.

For every detected issue, ArchSec should provide:

- The current weakness or outdated practice.
- The reason it matters.
- A recommended modern solution.
- Required tools, services, skills, and infrastructure.
- Estimated cost and effort.
- Migration steps.
- Security, reliability, and operational impact.
- Architecture diagrams, flow charts, or data-flow diagrams when useful.
- Priority level and dependency order.

## Key Capabilities

### 1. Legacy System Intake

Users describe their existing system:

- Website or application type.
- Current backend, frontend, database, hosting, and deployment process.
- Authentication and user management.
- Testing process.
- Security testing process.
- Monitoring and logging.
- Manual workflows.
- AI usage or lack of AI integration.
- Budget, team size, risk tolerance, and migration constraints.

### 2. Modernization Gap Analysis

The AI engine identifies outdated or risky areas such as:

- Old frameworks, runtimes, libraries, or CMS versions.
- Manual deployment or lack of CI/CD.
- Missing automated tests.
- Weak security testing practices.
- No observability or incident visibility.
- Poor scalability or reliability.
- Lack of AI-enabled customer support, search, analytics, automation, or internal tooling.
- Expensive or inefficient infrastructure.

### 3. Issue-by-Issue Recommendations

The platform should not return one large undifferentiated answer. It should produce structured findings where each issue has its own solution package:

- Issue title.
- Current state.
- Impact.
- Recommended future state.
- Tools and technologies.
- Cost estimate.
- Implementation requirements.
- Migration plan.
- Risks and mitigations.
- Expected benefits.

### 4. Modern Architecture Proposals

ArchSec recommends updated architectures such as:

- Cloud-hosted web applications.
- Containerized deployments.
- Managed databases and object storage.
- API-first systems.
- CI/CD pipelines.
- Automated test suites.
- Security gates with SAST, DAST, SCA, and secret scanning.
- Monitoring, logging, alerting, and backup strategies.
- AI integrations using LLM APIs, embeddings, retrieval, chat assistants, summarization, or workflow automation.

### 5. Cost, Effort, And Requirements

Each recommendation includes practical planning details:

- One-time migration cost.
- Monthly operating cost.
- Tooling/subscription cost.
- Required team skills.
- Development effort.
- Infrastructure changes.
- Phased rollout strategy.

### 6. Diagrams And Visual Planning

ArchSec generates diagrams that explain the migration:

- Current-state architecture.
- Proposed future-state architecture.
- Deployment pipeline flow.
- Data-flow diagrams.
- AI integration flow.
- Security testing workflow.
- Migration roadmap.

Mermaid is the primary diagram format.

### 7. Reports And History

Users can save modernization assessments, re-run analysis as details change, view previous assessments, and export reports for planning, budgeting, or client delivery.

## System Architecture

```text
User -> Django UI -> Project/System Intake -> AI Modernization Engine
     -> Issue Findings -> Recommendations/Costs/Diagrams
     -> Dashboard, History, Notifications, Reports
```

The current implementation uses Django templates, Celery, Redis, SQLite for development, Google Gemini-compatible AI generation, Mermaid diagrams, and PDF/Markdown/Text exports.

## Technology Stack

### Backend

- Python
- Django
- Celery + Redis
- SQLite for development
- PostgreSQL planned for production

### Frontend

- Django templates
- TailwindCSS via CDN
- Vanilla JavaScript
- Mermaid.js for diagrams

### AI

- Google Gemini API currently implemented.
- Prompting should evolve toward structured modernization findings.
- Future support can include OpenAI-compatible providers behind a provider abstraction.

### Reporting

- PDF export via WeasyPrint.
- Markdown and text export.
- ZIP export for analysis history.

## Current Implementation Status

Implemented:

- User authentication and ownership controls.
- Project/system intake.
- Structured project metadata using JSON fields.
- Async AI analysis with Celery.
- Security score and risk category.
- Analysis history.
- Notifications.
- Mermaid diagram storage and rendering.
- PDF, Markdown, Text, and ZIP exports.

Needs modernization-aligned updates:

- Rename product copy from secure planning to modernization advisory.
- Expand intake fields for legacy technology, deployment, testing, operations, and AI readiness.
- Change AI output schema from broad report sections to issue-by-issue modernization findings.
- Add cost/effort/requirements fields per issue.
- Add current-state and future-state diagrams.
- Update scoring to measure modernization priority, technical debt, AI readiness, and migration risk.
- Add JSON export and stronger response validation.
- Add production database configuration.
- Add real tests for analysis generation and permissions.

## Development Roadmap

### Phase 1 - Product Repositioning

- Update documentation and UI copy.
- Redesign the interface with a minimal modern look.
- Rename report language from "security analysis" to "modernization assessment."

### Phase 2 - Legacy System Intake

- Add fields for current stack age, hosting, deployment, testing, security testing, observability, data storage, integrations, and AI usage.
- Capture business constraints such as budget, downtime tolerance, compliance needs, and team skill level.

### Phase 3 - Structured Modernization Findings

- Update AI prompt and response schema.
- Store findings as structured JSON.
- Display each issue as an independent recommendation card.
- Include cost, effort, priority, dependencies, and migration steps per issue.

### Phase 4 - Architecture And Migration Planning

- Generate current-state and future-state architecture diagrams.
- Generate CI/CD, testing, security, and AI integration flows.
- Add phased migration roadmaps.

### Phase 5 - Reporting And Collaboration

- Export PDF, Markdown, JSON, and client-ready proposal formats.
- Add comparison between assessment versions.
- Add team review notes and decision tracking.

### Phase 6 - Reliability And Production Readiness

- Add response validation.
- Add automated tests.
- Add PostgreSQL production settings.
- Add provider abstraction for multiple AI APIs.
- Improve monitoring and operational health checks.

## Installation

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

For async analysis, Redis and a Celery worker are required.

```bash
celery -A planix worker -l info
```

## License

MIT License.
