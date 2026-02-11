# ArchSec Project Roadmap

This document outlines the development status and future roadmap for the ArchSec platform.

---

## Bugs
- [x] Fix NoReverseMatch: view_project URL resolution error
- [x] Fix incorrect redirect after analysis generation (should redirect to view_analysis)
- [x] Fix incorrect redirect behavior during aI failure path
- [x] Generate Analysis redirects to dashboard on AI model availability failure
- [x] Gemini API is never being called (AI client returns fallback error)
- [x] Django cannot find json_filters template tag library
- [x] Gemini model selection is not enforced to gemini-2.5-flash
- [x] Fix ValueError in AI analysis due to incorrect return signature
- [x] Suppress Pylance warning for missing `google-generativeai` package.
- [x] Gemini API is returning 'Too Many Requests' error.
- [x] Fix 429 quota error by preferring gemini-flash model.
- [x] Fix 'AI returned a non-JSON response' by enforcing JSON output mode.
- [x] Fix `no such column: core_projectanalysis.task_id` by running migrations.
- [x] Fix empty analysis page by providing a JSON schema in the AI prompt.
- [x] Fix asynchronous analysis job not displaying results
- [x] Mermaid diagrams not rendering in the analysis view.
- [ ] Mermaid diagrams are not rendering in the exported PDF.


---

## Features
- [x] Improve risk heatmap visualization with labels and better colors.
- [x] Enhance AI prompt to generate more detailed analysis.

---

## ✅ Completed Milestones (Phases 1-6)

- [x] Core Django project setup with a modular service-oriented architecture.
- [x] User authentication system for project and analysis ownership.
- [x] Advanced `Project` model using a flexible `JSONField` for structured architecture data.
- [x] `ProjectAnalysis` model for storing versioned, AI-generated security reports.
- [x] AI integration with the Google Gemini API for core analysis generation.
- [x] Hybrid security scoring engine combining rule-based checks with AI-driven risk adjustments.
- [x] AI-driven generation of Executive Summaries, Threat Models, and System Architecture.
- [x] Automated recommendations for Secure SDLC and security testing plans.
- [x] Risk category classification into Low, Medium, or High.
- [x] Analysis history tracking with risk trend visualization using Chart.js.
- [x] PDF and ZIP export capabilities for security reports and historical data.
- [x] Sophisticated, architecture-aware AI prompting engine.
- [x] Implement Terminal/Cyberpunk UI theme using TailwindCSS.

---

## 🚧 Identified Architectural Weaknesses

- **[COMPLETED] Fragile AI Response Parsing:** The current system relies on brittle markdown string parsing, which is susceptible to failures if the AI's output format deviates.
- **[COMPLETED] Synchronous AI Analysis:** Long-running AI analyses are executed as blocking HTTP requests, posing a risk of request timeouts and a poor user experience.
- **[COMPLETED] Data Model Anomaly:** A duplicate `executive_summary` field has been identified in the `ProjectAnalysis` model and requires a database schema cleanup.
---

## 🚀 Upcoming Development Roadmap

### PHASE 7 — Platform Hardening & Reliability
- [x] Migrate AI output from markdown to a structured JSON mode.
- [x] Replace all markdown parsing logic with robust JSON deserialization.
- [x] Refactor the `ai_client` service to support and enforce a JSON output schema.
- [ ] Implement an AI response validation layer to ensure data integrity.
- [x] Implement asynchronous AI processing for analysis jobs using Celery and Redis.
- [x] Add background job status tracking and reporting.
- [x] Implement frontend polling or WebSockets for real-time UI updates on analysis completion.
- [ ] Create a database migration to remove the duplicate `executive_summary` field.
- [ ] Add system health check endpoints for monitoring.
- [ ] Implement structured logging (e.g., JSON format) across the application.

### PHASE 8 — Compliance & Architecture Decision Engine
- [ ] Create a `ComplianceStandard` model (e.g., PCI DSS, ISO 27001, SOC2, HIPAA).
- [ ] Create a `ComplianceControl` model to store individual compliance requirements.
- [ ] Add functionality to map projects to one or more compliance frameworks.
- [ ] Enhance the AI engine to generate compliance evidence and identify gaps against selected controls.
- [ ] Build a compliance dashboard to visualize status and evidence.
- [ ] Implement an Architecture Decision Record (ADR) engine.
- [ ] Add versioning and history tracking for all ADRs.
- [ ] Generate AI-powered draft ADR documents from project architecture and decisions.
- [ ] Add export functionality for ADRs to Markdown and PDF.

### PHASE 9 — Proactive Intelligence & Maturity Scoring
- [ ] Implement a Security Maturity Model based on an industry standard (e.g., BSIMM or SAMM).
- [ ] Add multi-domain maturity scoring across areas like Governance, Design, and Operations.
- [ ] Create a radar chart visualization for security maturity scores.
- [ ] Implement AI-powered remediation suggestions, including actionable code samples.
- [ ] Add detection for common anti-patterns and vulnerability patterns in project architecture.
- [ ] Build a dedicated security knowledge base (e.g., using a vector database).
- [ ] Integrate Retrieval-Augmented Generation (RAG) for more accurate and verifiable AI reasoning.
- [ ] Implement reasoning traceability to show how the AI reached its conclusions.
- [ ] Add explainable AI (XAI) features to the analysis output.

### Phase 7B — Diagram Generation
- [x] Update ProjectAnalysis model to include diagram fields.
- [x] Update AI prompt to request Mermaid diagrams.
- [x] Save diagrams in generate_analysis.
- [x] Render diagrams in view_analysis.html.
- [x] Ensure diagrams are included in PDF export.
- [x] Update TODO.md with the new tasks.