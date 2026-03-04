# Disclosure Diagram Pack

**Title:** Disclosure Diagram Pack — Omniforge  
**Owner:** Matthew McCloskey  
**Version:** v1.0-draft  
**Date:** 2026-03-04  
**Intended Audience:** Security/IT, Legal/Compliance, Technical Reviewer

## Purpose

This document centralizes visual evidence for architecture, trust boundaries, and operational flows used in COI/CDI review.

## Reviewer Quick Start

Read first:
1. System Context
2. Trust-Boundary Data Flow
3. Top Workflow Sequences

Verify:
- Diagram steps align with CLI commands and module behavior
- External boundaries are explicitly shown

## Inputs Received

- Baseline diagrams: [EVIDENCE: docs/DIAGRAMS.md]
- Workflow and component definitions: [EVIDENCE: README.md → How It Works; CLI Surface]

---

## Diagram Index

| # | Diagram | Purpose | Evidence Anchor |
|---|---|---|---|
| 1 | System Context | Show actors + external boundaries | [EVIDENCE: README.md; docs/DIAGRAMS.md] |
| 2 | Trust-Boundary Data Flow | Show local vs external flow crossing | [EVIDENCE: docs/DIAGRAMS.md → High-Level Flow] |
| 3 | Export Workflow Sequence | Verify export lifecycle | [EVIDENCE: docs/DIAGRAMS.md → Exporter Detail] |
| 4 | Sanitizer Pipeline | Verify sanitization controls | [EVIDENCE: docs/DIAGRAMS.md → Sanitizer Pipeline] |
| 5 | Publish Workflow Sequence | Verify release path | [EVIDENCE: docs/DIAGRAMS.md → GitHub Publishing] |
| 6 | Telemetry Pipeline (current + future target) | Observability model for compliance reports | Current state uses local command-level telemetry; centralized backend remains a future control enhancement |
| 7 | Lightweight Threat View | Communicate top risk surfaces | [EVIDENCE: Architecture-Overview.md risk section] |

---

## 1) System Context

```mermaid
flowchart LR
		User[Personal Operator] --> CLI[Omniforge CLI]
		CLI --> LocalArtifacts[Local Artifacts + Docs]
		CLI --> SourceControl[Runndownn/Omniforge]
		CLI --> Webhook[Approved Personal Webhook Destination]
```

## 2) Trust-Boundary Data Flow

```mermaid
flowchart TD
		Input[settings.json + .zshrc] --> Process[Export/Sanitize]
		Process --> Artifacts[artifacts/* + manifest]
		Artifacts --> Apply[Apply/Restore]
		Artifacts --> Publish[Package/Release]
		Artifacts --> Broadcast[Webhook Broadcast]
		subgraph LocalBoundary
			Input
			Process
			Artifacts
			Apply
			Publish
		end
		subgraph ExternalBoundary
			Broadcast
			Source[(Remote Repos)]
		end
		Publish --> Source
```

## 3) Export Workflow Sequence

```mermaid
sequenceDiagram
	participant User
	participant CLI
	participant FS as FileSystem
	User->>CLI: Run export command
	CLI->>FS: Locate and read settings
	CLI->>FS: Copy redistributable assets
	CLI->>FS: Write artifacts/settings.json + manifest
	CLI-->>User: Success/failure status
```

## 4) Sanitizer Pipeline

```mermaid
flowchart LR
	S[Load .zshrc] --> R{Rule Engine}
	R -->|Drop| D[PII/tokens/abs paths/denylisted aliases]
	R -->|Keep| K[Theme, prompt, safe aliases]
	K --> O[Write zshrc.portable]
	D --> L[Sanitization report entry]
```

## 5) Publish Workflow Sequence

```mermaid
sequenceDiagram
	participant CLI
	participant Git
	CLI->>CLI: Build archive + release metadata
	CLI->>Git: Commit/tag (if enabled)
	CLI->>Git: Push (optional)
	Git-->>CLI: Status
```

## 6) Telemetry Pipeline (Current + Future Target)

```mermaid
flowchart LR
		Cmd[CLI Command] --> Log[Structured Command Logs]
		Cmd --> Metric[Run Metrics]
		Log --> Report[Monthly Evidence Report]
		Metric --> Report
```

Current documented state: centralized telemetry storage/dashboard tooling is not yet implemented for this project scope.

## 7) Lightweight Threat Model View

```mermaid
flowchart TD
		T1[Unsanitized output risk] --> M1[Sanitize-first + dry-run]
		T2[Destination misuse risk] --> M2[Webhook controls + review]
		T3[Resource mixing risk] --> M3[Separation checklist + attestation]
		T4[Dependency drift risk] --> M4[Test/lint cadence + SBOM optional]
```

