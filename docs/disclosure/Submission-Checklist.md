# Artifact 2 — Observability & Telemetry Pack

**Title:** Observability & Telemetry Pack — Omniforge  
**Owner:** Matthew McCloskey  
**Version:** v1.0-draft  
**Date:** 2026-03-04  
**Intended Audience:** Security/IT, Compliance/Legal, Technical Reviewer

## Purpose

This artifact defines what “healthy” looks like, what telemetry exists today, and which telemetry controls are targeted next, along with how monthly evidence is produced for compliance review and ongoing COI separation verification.

## Reviewer Quick Start

Read first:
1. Observability Goals
2. Instrumentation Map
3. Monthly Reporting Template

Verify:
- event coverage for critical workflows
- redaction behavior
- evidence archiving cadence

## Inputs Received

- CLI workflows and modules: [EVIDENCE: README.md → How It Works; CLI Surface]
- baseline flow diagrams: [EVIDENCE: docs/DIAGRAMS.md]
- messaging and sanitization code paths: [EVIDENCE: `tool/messaging.py`; `tool/sanitizer.py`]

---

## 1) Observability Goals

Healthy state:
- Export/sanitize/apply/package/broadcast flows execute without unhandled failures.
- Failure reasons are visible and attributable.
- Separation controls are attestable monthly.

Early warning signals:
- repeated webhook send failures
- sanitization rule failures or unexpected drops
- packaging failures and integrity drift

## 2) Telemetry Architecture

Current documented posture:
- command-level output and test validation are present.
- centralized metrics/tracing backend is not evidenced in provided inputs.

Status: **centralized telemetry backend not deployed in current scope**.

Minimal compliant plan:
1. Structured command logs (JSON line format)
2. Command duration and outcome counters
3. Monthly report export with evidence bundle

Current documented state: no centralized Prometheus/Grafana/OpenTelemetry stack is in use for this repo at this time.

## 3) Instrumentation Map per Component

| Component | Logs (event types + redaction) | Metrics (name/unit/tags) | Traces (span names/attrs) |
|---|---|---|---|
| Exporter | `export.start`, `export.complete`, `export.error`; redact user paths | `export_runs_total`, `export_duration_ms`, `export_failures_total` | `export.run` |
| Sanitizer | `sanitize.rule_applied`, `sanitize.output_written`; redact tokens/emails/paths | `sanitize_runs_total`, `sanitize_failures_total`, `sanitize_duration_ms` | `sanitize.run`, `sanitize.rules` |
| Messaging | `broadcast.chunk_sent`, `broadcast.error`; redact webhook secrets | `broadcast_messages_total`, `broadcast_errors_total`, `broadcast_latency_ms` + `service` tag | `broadcast.run`, `broadcast.send_chunk` |
| Publisher | `package.start`, `package.complete`, `package.error` | `package_runs_total`, `package_failures_total`, `package_duration_ms` | `package.run` |
| Applier | `apply.mode`, `apply.backup`, `apply.error` | `apply_runs_total`, `apply_failures_total`, `apply_duration_ms` | `apply.run` |

Cardinality cautions:
- avoid full file paths as metric labels
- avoid unbounded destination/URL labels

## 4) Dashboard Pack

| Dashboard | Key Panels | What it Proves |
|---|---|---|
| Reliability | success rate, failure rate, p95 runtime | platform run stability |
| Throughput | command counts, chunk counts, workflow volume | operational load and trend |
| Security Signals | sanitize drops, auth/network failures, anomaly counts | control effectiveness |
| Change Impact | release/version changes vs error shifts | safe-change discipline |

Security signal examples:
- auth failures to outbound endpoints
- repeated network errors by service mode
- denylisted alias removals and sanitize exceptions

## 5) Monthly Reporting Template (Copy/Paste)

```markdown
Month: YYYY-MM (for example: 2026-03)
Owner: Matthew McCloskey

1) Changes Shipped
- Commits/releases:
- Workflow/security-impacting changes:

2) Reliability
- Successful runs:
- Failed runs:
- Incidents:
- MTTR:

3) Security Events
- Sanitization anomalies:
- Outbound integration failures:
- Dependency findings and remediation:

4) Usage + Cost
- Run volume:
- Service usage:
- Cost summary:

5) Separation Controls Attestation
- Accounts separate: [Yes/No]
- Devices separate: [Yes/No]
- Networks separate: [Yes/No]
- Time boundary respected: [Yes/No]
- Evidence attached:

6) Next Actions
- Reliability actions:
- Security actions:
- Compliance follow-ups:
```

## 6) Recommended Diagram Set

- System context (actor + boundaries)
- Component model
- Trust-boundary data flow
- Top workflow sequences
- RBAC/authz view (not applicable in current single-operator model)
- Telemetry pipeline
- Lightweight threat model view

## Separation Controls Checklist (Operational Telemetry Lens)

| Control | Implemented? | Evidence | Notes |
|---|---|---|---|
| Telemetry redaction policy | Yes (documented and attested) | Sanitization and messaging controls documented in code/docs | Must exclude secrets/PII |
| Monthly evidence archive | Yes (documented and attested) | Monthly template and checklist included in this artifact | Required for review cadence |
| Alerting threshold definitions | Planned implementation (not yet deployed) | To be implemented with dashboard/alert rollout | Needed for early-warning proof |

## Risk Register (Telemetry Focus)

| Risk | Likelihood | Impact | Mitigation | Residual Risk | Evidence |
|---|---:|---:|---|---|---|
| Missing centralized telemetry | Medium | Medium | implement minimal structured logs + metrics | Low-Med | [EVIDENCE: current docs/code paths] |
| Sensitive fields in logs | Medium | High | strict redaction policy + test checks | Low-Med | Sanitization and messaging module behavior |
| No monthly evidence cadence | Medium | Medium | enforce monthly template + archive | Low | This artifact’s monthly reporting section |

---

## Submission Readiness Checklist

| Item | Status | Evidence Path |
|---|---|---|
| Artifact 1 complete | Ready for review | `docs/disclosure/Architecture-Overview.md` |
| Artifact 2 complete | Ready for review | `docs/disclosure/Submission-Checklist.md` |
| Artifact 3 complete | Ready for review | `docs/disclosure/COI-Disclosure.md` |
| Diagram pack attached | Ready for review | `docs/disclosure/Diagrams.md` |
| Prior inventions supplement | Ready for review | `docs/disclosure/Prior-Inventions.md` |
| Owner/legal metadata finalized | Done | Owner set to Matthew McCloskey in disclosure artifacts |
| Billing/tenant/account evidence attached | Pending owner attachment | Attach as supplemental proof packet |
| Employer policy references attached | Pending owner attachment | Add policy excerpt if shareable |

## Consolidated Evidence Actions (Prioritized)

1. **Owner/legal identity fields**  
	- Status: owner name finalized as Matthew McCloskey.  
	- Remaining: add title/contact and signature block format required by employer legal.

2. **Employer overlap classification**  
	- Current decision: adjacent but non-overlapping in this project scope.  
	- Remaining: obtain manager/legal concurrence in writing.

3. **Separation proof set (accounts/billing/tenant/device/network/time)**  
	- Action: attach ownership exports, billing statements, device/MDM status, VPN attestation, and time-boundary attestation.

4. **Repo visibility and commercialization status**  
	- Current decision: personal/non-commercial use in this packet.  
	- Action: attach visibility/export proof if requested by legal.

5. **Telemetry backend reality check**  
	- Current decision: centralized telemetry backend not deployed for this repo.  
	- Action: implement backend and attach dashboard proof only if required.

6. **`/ws` risk row applicability**  
	- Current decision: not applicable to current Omniforge scope (no websocket endpoint evidenced).  
	- Remaining: none unless future architecture adds websocket interfaces.

