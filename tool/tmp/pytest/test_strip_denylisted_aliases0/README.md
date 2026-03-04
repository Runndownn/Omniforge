# Test Fixture Workspace

Pytest materializes this directory while running `test_strip_denylisted_aliases`. The fixture mirrors the sanitizer output so assertions can inspect real files without touching your home directory.

```mermaid
flowchart TD
    TestCase["tests/test_sanitizer.py::test_strip_denylisted_aliases"] --> TmpDir["tmp_path factory"]
    TmpDir --> SampleZsh[".zshrc fixture"]
    SampleZsh --> Sanitizer["sanitize_zshrc(...)"]
    Sanitizer --> Portable["portable/zshrc.portable"]
    Sanitizer --> Manifest["manifest.json"]
    Portable --> Assertions
    Manifest --> Assertions
```

Delete this directory whenever you want to reclaim disk space; pytest recreates it on the next run.
