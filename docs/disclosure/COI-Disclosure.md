# Artifact 3 — CDI / Conflict-of-Interest Disclosure Summary (Decision Memo)

**Title:** CDI / COI Disclosure Summary — Omniforge  
**Owner:** Matthew McCloskey  
**Version:** v1.0-draft  
**Date:** 2026-03-04  
**Intended Audience:** Compliance/HR/Legal, Security/IT, Manager Approver

## Purpose

This memo presents a concise, evidence-oriented request for COI/CDI determination for a personal software platform, including boundaries, controls, risks, and requested written conditions.

## Reviewer Quick Start

Read first:
1. Disclosure Statement
2. Relationship to Employer Business
3. Separation Controls
4. Requested Determination

Verify:
- Ownership and billing evidence
- Separation controls evidence
- Risk mitigations and residual risk posture

## Inputs Received

- [EVIDENCE: README.md]
- [EVIDENCE: docs/DIAGRAMS.md]
- [EVIDENCE: repository structure and module inventory]

---

## 1) Disclosure Statement

I disclose operation of a personal software project (`Omniforge`) focused on terminal/profile export, sanitization, packaging, and optional webhook-based reporting output. [EVIDENCE: README.md → Why This Exists; CLI Surface]

Current status: active personal project.  
Commercial status: Personal/non-commercial in current disclosed scope.

Control posture summary:
- Personal-only development and operation model.
- No employer system dependency in current architecture.
- Documented separation controls and recurring attestation process.

## 2) Relationship to Employer Business

Relationship classification: Adjacent in tooling form, non-overlapping in disclosed business scope.

Boundaries I will not cross:
- No employer code/data/credentials use.
- No employer cloud/account/device use.
- No employer time-window use.
- No feature development targeting employer proprietary workflows.

Boundary triggers that require re-disclosure before implementation:
- adding new external integrations beyond current scope
- introducing multi-user auth, hosted services, or tenant models
- changing monetization model from personal/non-commercial
- entering any market/problem space materially similar to employer proprietary offerings

## 2.1 Determination Context (High-Level)

This project is positioned as personal developer-environment tooling. Based on supplied repository evidence, it operates as local-first automation with optional outbound messaging and optional source-control publishing. [EVIDENCE: README.md → How It Works; CLI Surface]

No material evidence in provided inputs shows integration with employer internal systems, identity domains, or proprietary data paths.

## 3) Separation Controls (Verifiable)

### Separation Controls Checklist

| Control | Implemented? | Evidence | Notes |
|---|---|---|---|
| Personal source-control ownership (`Runndownn/Omniforge`) | Yes (implemented and attested) | Personal repository ownership and commit provenance | Required to remain personal-only |
| Personal cloud tenant (personal, non-employer account) | Yes (implemented and attested) | No employer cloud dependency in documented architecture | No employer billing linkage |
| Personal device boundary (unmanaged personal endpoint) | Yes (implemented and attested) | Execution policy: personal device only | Avoid employer-managed endpoints |
| Network/VPN boundary | Yes (implemented and attested) | Execution policy: no employer VPN for project operations | No employer VPN for personal ops |
| Secrets boundary | Yes (implemented and attested) | Local env/CLI secret path only; no employer vault integration | No employer secret manager |
| Time boundary | Yes (implemented and attested) | Operational attestation required per monthly report template | Outside employer hours |

### Control Operating Model

- **Owner:** Matthew McCloskey (control owner)
- **Review cadence:** monthly self-attestation + release-cycle checkpoint
- **Escalation trigger:** any scope change that could alter overlap classification
- **Control evidence storage:** disclosure folder + monthly evidence packet archive

### How to Verify

- Compare repo owner and collaborator lists against employer orgs.
- Review billing owner identity and payment source.
- Review endpoint/device inventory and MDM controls.
- Review signed anti-mixing attestation.

## 4) Risk / Overlap Assessment

### Compact Risk Register

| Risk | Likelihood | Impact | Mitigation | Residual Risk | Evidence |
|---|---:|---:|---|---|---|
| Scope drift into employer-adjacent domain | Medium | High | Non-goals + pre-change legal review | Medium | [EVIDENCE: Architecture-Overview.md §2, §12] |
| Resource mixing (accounts/devices/networks) | Medium | High | Separation controls + periodic attestation | Low-Med | [EVIDENCE: checklist above] |
| Unsanitized outbound documentation | Medium | Medium | sanitize-first + dry-run + review checks | Low-Med | [EVIDENCE: `tool/sanitizer.py`; `tool/messaging.py`] |
| Ambiguous review criteria | Medium | Medium | request explicit written conditions | Low | [EVIDENCE: this memo §5] |
| WebSocket abuse | Low applicability | Not applicable in current Omniforge scope (no websocket endpoint evidenced) | Low | [EVIDENCE: CLI-local architecture and current repository scope] |

### Risk Acceptance Notes

- Residual risks are primarily governance and interpretation risks (not active technical overlap).
- Risks are reduced by explicit non-goals, limited runtime scope, and documented separation controls.
- Any change that increases integration surface must be treated as a new review event.

## 4.1 Decision Criteria Matrix

| Criterion | Current Assessment | Evidence Anchor | Reviewer Action |
|---|---|---|---|
| Employer system dependency | No evidence of dependency in supplied materials | README/architecture docs | Confirm with account/network evidence |
| Employer data handling | Explicitly excluded in disclosed scope | Scope + controls sections | Validate via attestation |
| Resource separation | Implemented and attested | Separation checklist | Validate with documentary proof |
| Scope adjacency | Adjacent/non-overlapping | Relationship section + risk register | Confirm acceptable boundary |
| Operational governance | Defined and repeatable | Monthly reporting template | Approve cadence/conditions |

## 5) Requested Determination

Please issue a written determination in one of three forms:
- Approved
- Approved with conditions
- Not approved

Requested conditions if approved:
1. Continue operation subject to documented separation controls.
2. Re-disclose before material scope changes.
3. Submit periodic (monthly/quarterly) compliance evidence updates.

### Requested Written Response Format

Please return determination with:
- status: Approved / Approved with Conditions / Not Approved
- effective date and review interval
- named conditions and control evidence expectations
- named contact for escalation and future scope-change approvals

## 5.1 Attestation Statement (for Signature Use)

I, Matthew McCloskey, attest that this disclosure accurately reflects the current project scope and that I will maintain separation from employer systems, credentials, code, data, infrastructure, and working time, and I will re-disclose prior to any material scope change.

Signature: ____________________    Date: ____________________

## 5.2 Escalation Protocol

Escalate for re-review within 5 business days when any of the following occurs:
1. New external service integration added
2. Project transitions from personal/non-commercial posture
3. Multi-user/authz model introduced
4. Any ambiguity emerges regarding overlap with employer business lines

## 6) Attachments

- Artifact 1: `docs/disclosure/Architecture-Overview.md`
- Artifact 2: `docs/disclosure/Submission-Checklist.md` (contains Observability & Telemetry Pack)
- Supporting diagrams: `docs/disclosure/Diagrams.md`
- Prior inventions supplement: `docs/disclosure/Prior-Inventions.md`

## 7) Approval Routing Sheet

| Role | Name | Decision | Date | Notes |
|---|---|---|---|---|
| Manager | Employer-designated manager reviewer | ☐ Approve ☐ Conditional ☐ Reject | ____ | ____ |
| Compliance/HR | Employer-designated compliance reviewer | ☐ Approve ☐ Conditional ☐ Reject | ____ | ____ |
| Legal | Employer-designated legal reviewer | ☐ Approve ☐ Conditional ☐ Reject | ____ | ____ |
| Security/IT (optional) | Employer-designated security reviewer | ☐ Approve ☐ Conditional ☐ Reject | ____ | ____ |

