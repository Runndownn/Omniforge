# CI/CD Workflows

The repository currently ships a single workflow, `release.yml`, which packages artifacts and prepares a GitHub release. Future automations should document their behavior here.

```mermaid
sequenceDiagram
    participant Dev as Maintainer
    participant GH as GitHub Actions
    participant Job as release.yml
    participant CLI as tool.cli
    Dev->>GH: Create tag / dispatch workflow
    GH->>Job: Start build matrix
    Job->>CLI: python -m tool.cli package --version <tag>
    CLI-->>Job: release/portable-profile.zip
    Job->>GH: Upload artifact + draft notes
    GH-->>Dev: Release artifacts available
```

Key stages:

1. **Build** — installs dependencies, runs Ruff, mypy, and pytest.
2. **Package** — invokes the CLI to generate the release bundle and JSON descriptor.
3. **Publish** — uploads artifacts for manual verification before pushing tags.
