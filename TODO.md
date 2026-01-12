# ArchSec Project TODO

This file tracks the development progress based on the phases outlined in the `README.md`.

---

### Database Schema Hotfix (2026-01-12)
- **Status:** Partially Complete
- **Tasks:**
    - [x] Inspect `core/models/project.py` for `structured_data` field.
    - [x] Confirm `Project` model has `JSONField` for `structured_data`.
    - [x] Manually create migration `0010_auto_20260112_1200.py` for the missing column.
    - [ ] Apply the new migration to the database.
    - [ ] Verify the dashboard and ORM queries work as expected.
- **Notes:**
    - The `run_shell_command` tool is disabled in the current environment, so the `migrate` command could not be run. The migration file has been created, but the database schema has not been updated. The user will need to run `python manage.py migrate` to apply the changes.

---

### Phase 1: Environment & Base Setup (Week 1) ✅
- **Status:** Mostly Complete
- **Tasks:**
    - [x] Create GitHub repo
    - [x] Configure GitHub Codespaces
    - [x] Initialize Django project
    - [x] User authentication setup
    - [x] Base UI + dashboard shell
    - [x] Connect AI API keys via environment variables

---

### Phase 2: Project Creation + AI Design Engine (Week 2–3) ✅
- **Status:** Largely Complete
- **Tasks:**
    - [x] Create new project
    - [x] Input project info: tech stack, platform, budget, risk level
    - [x] AI generates:
        - [x] System design
        - [x] Architecture
        - [x] Tech suggestions
        - [x] Initial security risks
        - [x] Rough cost estimation

---

### Phase 3: Security Intelligence Module (Week 4–5) ✅
- **Status:** Largely Complete
- **Tasks:**
    - [x] Add full AI-driven modules:
        - [x] Threat modeling (STRIDE/DREAD)
        - [x] Attack vector identification
        - [x] Security measures & countermeasures
        - [x] Secure SDLC guidelines
        - [ ] Suggest compliance frameworks (OWASP ASVS, ISO 27001, NIST 800-53) - *Note: Basic OWASP Top 10 is mentioned, but not the others.*

---

### Phase 4: Testing & Audit Planning Module (Week 6) ✅
- **Status:** Largely Complete
- **Tasks:**
    - [x] Implement:
        - [x] AI-generated penetration test plan
        - [x] Recommended security tools (Nmap, Burp, ZAP)
        - [ ] Secure coding checklist - *Note: Not explicitly generated.*
        - [ ] Test case generation - *Note: Not explicitly generated.*
        - [x] Severity scoring (CVSS-like) - *Note: A custom security score is implemented.*

---

### Phase 5: Reporting & Export Module (Week 7–8)
- **Status:** Partially Complete
- **Tasks:**
    - [x] Export project reports as:
        - [x] PDF
        - [x] Markdown
        - [ ] JSON - *Note: Not implemented.*
    - [ ] Architecture diagrams using Mermaid
    - [x] Dashboard overview for all projects

---

### Phase 6: UI Improvement & Final Integration (Week 9)
- **Status:** Partially Complete
- **Tasks:**
    - [ ] Modern UI polishing - *Note: Uses Bootstrap, not TailwindCSS as planned. UI needs refinement.*
    - [ ] Nav sidebar + clean components
    - [ ] Better readability for long AI outputs
    - [x] Project history & logs
    - [ ] Error handling & response caching

---

### Phase 7: Testing & Deployment (Week 10)
- **Status:** Not Started
- **Tasks:**
    - [ ] Unit testing + integration testing
    - [ ] Performance checks
    - [ ] Deploy on:
        - [ ] Render
        - [ ] Railway
        - [ ] Or Django + PostgreSQL hosting

---

### Project Idea Submission Module Upgrade
- **Status:** Not Started
- **Tasks:**
    - [x] **1. Update Project model:**
        - [x] Use JSONField to store structured sections:
            - `requirements`, `users`, `architecture`, `technology`, `security`,
            - `performance`, `database`, `testing`, `deployment`, `monitoring`,
            - `compliance`, `privacy`, `scalability`, `infrastructure`
        - [x] Keep backward compatibility
    - [x] **2. Update project creation form:**
        - [x] For each section, provide common selectable options
        - [x] Provide an optional input field
        - [x] Group inputs logically
    - [x] **3. Update project creation template:**
        - [x] Use sectioned UI (accordion or fieldsets)
        - [x] Keep it readable and not overwhelming
    - [x] **4. Update project save logic:**
        - [x] Merge dropdown + manual inputs correctly into JSON fields
    - [x] **5. Update AI analysis prompt:**
        - [x] Pass structured data with clear section headers
        - [x] Do not flatten JSON into plain text
    - [x] **6. Update security scoring logic:**
        - [x] Penalize missing security/monitoring/compliance data
        - [x] Reward mature architecture choices
    - [x] **7. Update dashboard:**
        - [x] Show completeness indicators
        - [x] Warn for missing critical sections
    - [x] **8. Update TODO.md:**
        - [x] Add all above tasks
        - [x] Mark completed tasks clearly
