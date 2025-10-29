# GitHub Configuration

Project automation lives under `.github`. Workflows publish releases and enforce quality gates based on the portable profile lifecycle.

```mermaid
flowchart TD
    Trigger["Tag push or manual dispatch"] --> ReleaseWorkflow["workflows/release.yml"]
    ReleaseWorkflow --> Checkout["actions/checkout"]
    ReleaseWorkflow --> PythonSetup["actions/setup-python"]
    PythonSetup --> Build["make lint test"]
    Build --> Package["tool.github_publisher.publish"]
    Package --> Upload["actions/upload-artifact"]
```

Refer to `.github/workflows/README.md` for step-by-step explanations of each job.
