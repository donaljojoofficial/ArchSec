# ArchSec Project Roadmap

This document outlines the development status and future roadmap for the ArchSec platform.

---

## Bugs
- [x] Fix NoReverseMatch: view_project URL resolution error
- [x] Fix incorrect redirect after analysis generation (should redirect to view_analysis)
- [x] Fix incorrect redirect behavior during AI failure path
- [x] Generate Analysis always redirects to dashboard even on success

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

---

## 🚧 Identified Architectural Weaknesses

- **Fragile AI Response Parsing:** The current system relies on brittle markdown string parsing, which is susceptible to failures if the AI's output format deviates.
- **Synchronous AI Analysis:** Long-running AI analyses are executed as blocking HTTP requests, posing a risk of request timeouts and a poor user experience.
- **Data Model Anomaly:** A duplicate `executive_summary` field has been identified in the `ProjectAnalysis` model and requires a database schema cleanup.

---

## 🚀 Upcoming Development Roadmap

### PHASE 7 — Platform Hardening & Reliability
- [ ] Migrate AI output from markdown to a structured JSON mode.
- [ ] Replace all markdown parsing logic with robust JSON deserialization.
- [ ] Refactor the `ai_client` service to support and enforce a JSON output schema.
- [ ] Implement an AI response validation layer to ensure data integrity.
- [ ] Implement asynchronous AI processing for analysis jobs using Celery and Redis.
- [ ] Add background job status tracking and reporting.
- [ ] Implement frontend polling or WebSockets for real-time UI updates on analysis completion.
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