# Search Queries for Job Scraper

<!-- SETUP: Customize these queries based on your skills, target roles, and location -->

## Installed portal CLIs (primary for `/scrape`)

`/scrape` discovers every portal skill under `.agents/skills/*/SKILL.md` and runs its CLI first. Shipped country-agnostic CLIs include `linkedin-search` and `freehire-search`; Danish demos and any skill you add with `/add-portal` are included the same way. You do **not** need a matching `site:` line below for those CLIs to run.

The `site:` query templates in this file are the **WebSearch fallback** — for portals without a CLI, company career pages, or when a CLI fails.

## Search Sites

Primary (Markus is fully remote/international - LinkedIn is the main lever; no local job board configured yet):
- **linkedin.com/jobs** - primary search surface, covered by the `linkedin-search` CLI; no city filter needed since scope is fully remote/international
- No German/European board (StepStone, Xing, etc.) configured yet - run `/add-portal` if Markus wants one added later

Secondary (company career pages via Google):
- Direct Google searches with `site:` filters for known target companies (past applications include CrowdStrike, ServiceNow, Cohesity, Check Point, Coupa)

## Query Categories

Queries are grouped by priority. Location is intentionally omitted from most queries since the search scope is fully remote/international, not commute-bound.

### Priority 1: Global Head of Solution Consulting / VP-level Presales Leadership

These match Markus's strongest and most desired career direction.

```
site:linkedin.com/jobs "Global Head of Solution Consulting"
site:linkedin.com/jobs "VP Solutions Engineering"
site:linkedin.com/jobs "VP Sales Engineering"
```

### Priority 2: Senior Director / Presales Leadership

Adjacent seniority levels in the same functional lane.

```
site:linkedin.com/jobs "Senior Director Sales Engineering"
site:linkedin.com/jobs "Presales Leader"
site:linkedin.com/jobs "Presales Leadership" remote
```

### Priority 3: Security & Identity Domain Presales

Roles where the security/identity domain expertise is the primary draw.

```
site:linkedin.com/jobs "Solutions Engineering" "identity and access management" director OR VP
site:linkedin.com/jobs "Sales Engineering" "Zero Trust" leader
```

### Priority 4: Interim / Advisory Engagements

Broader net for interim executive and advisory work, matching current self-employed positioning.

```
site:linkedin.com/jobs "Interim" "Solutions Engineering" leadership
site:linkedin.com/jobs "Presales" advisor OR consultant remote
```

## Location Filter

Scope is fully remote/international - no commute-distance filtering applies. Verify instead that:
- The role is explicitly remote-friendly, or does not require relocation abroad (deal-breaker - see CLAUDE.md)
- Frequent international travel requirements are flagged for discussion, not auto-rejected

## Date Filter

Only include jobs posted within the last 14 days, or with an application deadline that has not yet passed. If a posting date cannot be determined, include it but flag as "date unknown".

## Adapting Queries

If the user specifies a focus area, select queries from the matching category and also generate 2-3 custom queries for that focus. For example:
- "/scrape [focus_area]" -> relevant category queries + custom focus-specific queries
