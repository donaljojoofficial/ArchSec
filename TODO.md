# ArchSec Modernization Roadmap

This roadmap reflects the new product direction: ArchSec is now an AI Modernization Advisor for legacy websites, outdated systems, traditional deployment workflows, manual testing practices, and organizations that have not yet integrated AI into their operations.

## Completed Foundation

- [x] Django application foundation.
- [x] User authentication and project ownership.
- [x] Project/system intake flow.
- [x] Structured metadata storage with JSON fields.
- [x] Async AI analysis through Celery and Redis.
- [x] Gemini-based AI client.
- [x] Analysis history.
- [x] Notifications.
- [x] Mermaid diagram fields.
- [x] PDF, Markdown, Text, and ZIP exports.
- [x] Health check endpoint.
- [x] Structured logging setup.

## Product Pivot Tasks

- [x] Rewrite README around legacy modernization and AI-readiness advisory.
- [x] Rewrite TODO roadmap around modernization assessments.
- [x] Add root implementation summary for the new direction.
- [x] Replace old "secure planning assistant" terminology throughout primary UI and prompts.
- [x] Rename analysis labels to "modernization assessment" where appropriate.
- [ ] Decide whether the brand remains ArchSec or becomes a broader modernization brand.

## Authorization And Isolation

- [x] Keep regular dashboard data scoped to the logged-in user's systems.
- [x] Protect project and assessment views with ownership checks.
- [x] Restrict Celery/task monitor access to admin users only.
- [x] Hide task monitor and user administration links from non-admin users.
- [x] Add tests for project isolation, assessment isolation, and admin-only task monitor access.

## Phase 1 - Minimal Modern UI Redesign

- [x] Replace the terminal/cyberpunk visual style with a minimal modern interface.
- [x] Update shared layout, navigation, buttons, forms, cards, and status states.
- [x] Redesign dashboard around systems, assessments, modernization priority, and recent findings.
- [x] Redesign project creation as a legacy system profile intake.
- [x] Redesign report pages around issue-by-issue recommendations.
- [ ] Keep pages responsive on mobile and desktop.

## Phase 2 - Legacy System Intake Model

- [ ] Add intake fields for current backend, frontend, CMS/framework, database, hosting, and deployment method.
- [ ] Add fields for runtime/framework age and version notes.
- [ ] Add fields for current testing process, automation level, and coverage.
- [ ] Add fields for security testing process: SAST, DAST, SCA, pentest, secrets, dependency scanning.
- [ ] Add fields for monitoring, logging, alerting, backups, and incident response.
- [x] Add first-pass fields for AI readiness: existing AI usage, candidate workflows, data availability, privacy constraints.
- [ ] Add migration constraints: budget, timeline, downtime tolerance, team skill level, compliance needs.
- [ ] Update dashboard completeness checks to use modernization-critical sections.

## Phase 3 - Issue-Based AI Output

- [ ] Replace broad report schema with structured findings.
- [ ] Each finding should include title, category, current issue, impact, recommendation, cost estimate, effort, requirements, migration steps, dependencies, risks, expected benefits, and priority.
- [ ] Add top-level modernization score, AI-readiness score, technical-debt score, security-risk score, and migration-risk score.
- [ ] Store structured findings in `ProjectAnalysis.raw_ai_response`.
- [ ] Add normalized database models later if reporting/searching across findings becomes important.
- [ ] Add AI response validation before saving.
- [ ] Add graceful handling for incomplete or malformed AI responses.

## Phase 4 - Modernization Diagrams

- [ ] Generate current-state architecture diagrams.
- [ ] Generate proposed future-state architecture diagrams.
- [ ] Generate deployment pipeline flow charts.
- [ ] Generate security testing workflow diagrams.
- [ ] Generate AI integration flow charts.
- [ ] Generate phased migration roadmap diagrams.
- [ ] Update PDF export so diagrams render reliably.

## Phase 5 - Cost And Migration Planning

- [ ] Add cost ranges per recommendation.
- [ ] Add monthly operating cost estimates.
- [ ] Add required tools and subscription assumptions.
- [ ] Add skill and staffing requirements.
- [ ] Add phased rollout plans: quick wins, medium-term, long-term.
- [ ] Add dependency ordering between recommendations.
- [ ] Add version-to-version comparison for repeated assessments.

## Phase 6 - Reports And Exports

- [ ] Update PDF report to match modernization assessment structure.
- [ ] Add JSON export for structured findings.
- [ ] Add client-ready proposal export.
- [ ] Add executive summary organized by business impact.
- [ ] Add roadmap summary organized by time and cost.
- [ ] Add appendix for raw AI response and diagrams.

## Phase 7 - Reliability And Production Readiness

- [ ] Add automated tests for forms, permissions, analysis views, exports, and AI parsing.
- [ ] Add mocked AI tests for predictable report generation.
- [ ] Add PostgreSQL production database configuration.
- [ ] Move sensitive settings fully into environment variables.
- [ ] Add AI provider abstraction for Gemini, OpenAI-compatible APIs, and local models.
- [ ] Add retry/backoff controls and clearer job failure states.
- [ ] Add monitoring for Celery task failures and AI quota errors.

## Known Technical Issues

- [ ] `ProjectAnalysis.sdls_recommendations` should eventually be renamed to `sdlc_recommendations`.
- [ ] `core/tests.py` is effectively empty.
- [ ] DRF is installed but no real API surface exists yet.
- [ ] PDF Mermaid rendering through WeasyPrint may not execute JavaScript reliably.
- [ ] `SECRET_KEY`, `ALLOWED_HOSTS`, and production database settings need hardening before deployment.
