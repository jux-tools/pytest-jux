# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.2] - 2026-09-26

First release carrying the 0.6.1 security fix to PyPI.

### Security

- Refresh `uv.lock` (73 packages). The lockfile pinned versions with known advisories —
  `requests` 2.32.5 (PYSEC-2026-2275), `urllib3` 2.6.3 (PYSEC-2026-141, PYSEC-2026-142),
  `soupsieve` 2.8, `virtualenv` 20.35.3 — which the development and CI environments installed
  and the scheduled security scan reported. The published package was not affected: a fresh
  install resolves current releases
- Known and unfixed: `nltk` 3.10.3 (PYSEC-2026-3740), pulled in by `safety` through the optional
  `security` extra; no fixed release exists yet

## [0.6.1] - 2026-09-26

Tagged but never published to PyPI; see 0.6.2.

### Security

- Require `cryptography>=46.0.5` (was `>=41.0`) so an install can no longer resolve a version
  affected by CVE-2026-26007 (GHSA-r6ph-v2qm-q3c2), a subgroup attack on SECT curves caused by
  missing subgroup validation. The lockfile already pinned 46.0.5, but the lockfile does not
  ship in the package
- Require `py-juxlib>=0.3.3`, which carries the same floor

### Fixed

- Release workflow: pin `pypa/gh-action-pypi-publish` to v1.14.2, whose twine accepts the
  `Metadata-Version: 2.5` that current hatchling writes
- Tests: `jux-sign` stdout tests replace `sys.stdout` with a real stream instead of a `Mock`,
  which Python 3.14's argparse rejected when probing `fileno()` for colour support; `jux-inspect`
  tests strip ANSI styling, so they pass when `FORCE_COLOR` is set

### Changed

- Migrated GitHub URLs to the jux-tools organization
- Adopted the two-stage pre-commit pattern
- Updated the C4 architecture model for the py-juxlib dependency

## [0.6.0] - 2026-02-12

### Changed

- **BREAKING (internal)**: Migrated all core modules to py-juxlib shared library (Sprint 9)
  - `metadata.py` → thin wrapper around `juxlib.metadata`
  - `signer.py` → re-exports from `juxlib.signing`
  - `verifier.py` → re-exports from `juxlib.signing`
  - `canonicalizer.py` → re-exports from `juxlib.signing`
  - `api_client.py` → re-exports from `juxlib.api`
  - `config.py` → re-exports from `juxlib.config`
  - `storage.py` → re-exports from `juxlib.storage`
- Public API unchanged — all existing import paths still work
- ~70% code reduction in migrated modules (~1,100 lines removed)
- Single-source versioning via `importlib.metadata` (pyproject.toml is source of truth)

### Added

- `py-juxlib>=0.3.0` as runtime dependency
- 16 additional tests since v0.4.3

### Fixed

- Version mismatch between `__init__.py` and `pyproject.toml`

### Technical Details

- **Sprint**: 9 (py-juxlib migration)
- **Story Points**: 21
- **Tests**: 439 passed, 17 skipped, 16 xfailed
- **Dependency**: py-juxlib v0.3.0+ (errors, metadata, signing, config, storage, api)

## [0.4.3] - 2026-01-19

### Changed
- Requires py-juxlib v0.2.1 (breaking change in PublishResponse model)
- Updated all code to use `response.test_run_id` instead of `response.test_run.id`

### Added
- **Sprint 8 (Integration Testing with jux-mock-server) - Complete**
- **Integration Test Suite** (`tests/integration/`):
  - `test_api_publishing.py` - Comprehensive API publishing integration tests
  - Uses jux-mock-server v0.5.0 LiveMockServer for real HTTP testing
  - Tests skip gracefully when jux-mock-server not installed
- **TestJuxAPIClientIntegration** (4 tests):
  - `test_publish_report_success` - Successful report publishing
  - `test_publish_report_with_bearer_token` - Bearer token authentication
  - `test_publish_report_server_error` - Server error handling (503)
  - `test_publish_report_captures_xml_content` - XML content verification
- **TestPublishCommandIntegration** (4 tests):
  - `test_publish_single_file_success` - Single file publishing
  - `test_publish_with_bearer_token` - CLI bearer token support
  - `test_publish_server_error_returns_nonzero` - Error exit codes
  - `test_publish_json_output` - JSON output format
- **TestPluginIntegration** (3 tests):
  - `test_plugin_publishes_on_session_finish` - Automatic publishing on session end
  - `test_plugin_publishes_with_api_storage_mode` - API storage mode publishing
  - `test_plugin_handles_server_error_gracefully` - Graceful error handling
- **Test Fixtures** (`tests/conftest.py`):
  - `live_mock_server` fixture for LiveMockServer
  - `sample_junit_xml` fixture for test data
  - `integration` pytest marker registered in pyproject.toml

### Changed
- Updated to py-juxlib v0.2.0 PublishResponse format (jux-openapi compliant)
- Plugin and publish command now use `response.test_run_id` and `response.success_rate`

### Tests
- 423 tests passing (+3 from integration tests), 17 skipped, 16 xfailed
- 11 new integration tests covering full API publishing flow
- Integration tests require jux-mock-server v0.5.0+ (optional dev dependency)

## [0.4.2] - 2026-01-19

### Changed
- Updated to py-juxlib v0.2.0 PublishResponse format (jux-openapi SubmitResponse compliant)
- Plugin now uses `response.test_run_id` instead of `response.test_run.id`
- Plugin now uses `response.success_rate` instead of `response.test_run.success_rate`
- Publish command updated for new response format

### Fixed
- Compatibility with py-juxlib v0.2.0 model changes

## [0.4.1] - 2026-01-08

### Added
- **C4 Architecture Model Enhancements**:
  - Added `pytest` as external system (was missing from model)
  - Updated relationships: Developer → pytest → pytest-jux → Jux API
  - Updated TestExecutionFlow dynamic view with pytest hook invocation
  - Static HTML export (`docs/architecture/static/`) for offline viewing
  - JSON export (`docs/architecture/workspace.json`) for tooling integration

### Changed
- Updated all documentation version references from v0.2.0/v0.3.0 to v0.4.0
- Updated documentation dates to 2026-01-08
- Added `jux-publish` command examples to README CLI section
- Updated project structure in README with Sprint 4 files
- Marked Sprint 4 as complete in ROADMAP.md

### Documentation
- Updated `docs/index.md` version to v0.4.0
- Updated `docs/NAVIGATION.md` version to v0.4.0
- Updated `docs/ROADMAP.md` with Sprint 4 completion status
- Updated `docs/sprints/sprint-04-api-integration.md` deliverables to v0.4.0

## [0.4.0] - 2026-01-08

### Added
- **Sprint 4 (REST API Client & Plugin Integration) - Complete**
- **REST API Client** (`pytest_jux.api_client`):
  - `JuxAPIClient` class for Jux API v1.0.0 `/junit/submit` endpoint
  - Bearer token authentication (Authorization header)
  - Retry logic with exponential backoff (1s, 2s, 4s)
  - Comprehensive error handling (4xx/5xx, network errors, timeouts)
  - `PublishResponse` and `TestRun` Pydantic models for response parsing
  - 13 unit tests with mocked HTTP responses (92.86% coverage)
- **Plugin Integration** with API publishing:
  - Automatic report publishing in `pytest_sessionfinish` hook
  - All storage modes supported: LOCAL, API, BOTH, CACHE
  - Graceful degradation on network failures
  - Error handling with pytest warnings (non-blocking)
  - 6 comprehensive plugin tests for API publishing scenarios
- **Manual Publishing Command** (`jux-publish`):
  - Single file mode: `jux-publish --file report.xml --api-url <url>`
  - Queue mode: `jux-publish --queue --api-url <url>`
  - Dry-run mode: `--dry-run` to preview without publishing
  - JSON output: `--json` for scripting integration
  - Verbose mode: `--verbose` for detailed progress
  - Authentication: `--bearer-token` for remote API access
  - Configuration: `--timeout` and `--max-retries` options
  - Exit codes: 0 (success), 1 (all failed), 2 (partial success)
  - 20 comprehensive tests (78.86% coverage)
- **New Configuration Options** (CLI and environment variables):
  - `--jux-api-url` / `JUX_API_URL` - Jux API base URL
  - `--jux-bearer-token` / `JUX_BEARER_TOKEN` - Bearer token for authentication
  - `--jux-api-timeout` / `JUX_API_TIMEOUT` - Request timeout (default: 30s)
  - `--jux-api-max-retries` / `JUX_API_MAX_RETRIES` - Max retry attempts (default: 3)

### Changed
- Organized release notes in `docs/release-notes/` directory structure
- Added "Releases" section to README.md with links to release notes

### Fixed
- Resolved 12 mypy type checking errors
- Resolved 13 ruff linting errors
- Added `configargparse` to mypy ignore_missing_imports
- Updated deprecated `strict_concatenate` → `extra_checks` in mypy config
- Fixed `any` → `Any` type annotation in metadata.py
- Added type guards for plugin API publishing

### Tests
- 420 tests passing (60 new), 9 skipped, 16 xfailed
- Overall coverage: 86.68% (above 85% target)
- api_client.py: 92.86% coverage
- publish.py: 78.86% coverage

### Documentation
- Sprint 4 documentation updated with all completed user stories
- CLI reference updated with `jux-publish` command

## [0.3.0] - 2025-10-24

### Changed
- **BREAKING CHANGE: Metadata Storage Architecture** (ADR-0011):
  - Environment metadata now embedded in JUnit XML `<properties>` elements (was: separate JSON sidecar files)
  - All metadata cryptographically signed with XMLDSig (was: JSON files not signed)
  - Added `pytest_metadata()` hook to inject environment metadata into pytest-metadata
  - Semantic namespace prefixes for metadata organization (jux:, git:, ci:, env:)
  - Single source of truth: All metadata in XML file (no more separate `.json` files)
- **BREAKING CHANGE: Storage Structure**:
  - Removed `metadata/` directory (metadata now in XML `<properties>`)
  - Storage structure simplified: `reports/{hash}.xml` and `queue/{hash}.xml` only
  - `storage.store_report()` signature changed: removed `metadata` parameter
  - `storage.get_metadata()` method removed (read from XML properties instead)
  - `storage.queue_report()` signature changed: removed `metadata` parameter
  - `storage.delete_report()` no longer deletes separate metadata files

### Added
- **Sprint 7 (Metadata Integration with pytest-metadata) - Complete**
- `pytest_metadata()` hook in `plugin.py` to inject environment metadata
- **Project Name Capture** (mandatory field):
  - Auto-detected from git remote URL (extracts repository name)
  - Or read from `pyproject.toml` ([project] name or [tool.poetry] name)
  - Or from `JUX_PROJECT_NAME` environment variable
  - Or falls back to current directory name
  - Injected as `<property name="project" value="..."/>` (no namespace prefix)
- **Core Metadata Properties** (jux: prefix):
  - `jux:hostname` - Hostname where tests executed
  - `jux:username` - Username running tests
  - `jux:platform` - Platform/OS information
  - `jux:python_version` - Python version
  - `jux:pytest_version` - pytest version
  - `jux:pytest_jux_version` - pytest-jux version
  - `jux:timestamp` - Execution timestamp (ISO 8601 UTC)
- **Git Metadata** (git: prefix) - Auto-detected:
  - `git:commit` - Git commit SHA (full)
  - `git:branch` - Current branch name
  - `git:status` - Working tree status ("clean" or "dirty")
  - `git:remote` - Git remote URL (credentials sanitized)
  - Multi-remote support (tries origin, home, upstream, github, gitlab)
  - Automatic credential sanitization for remote URLs
- **CI Metadata** (ci: prefix) - Auto-detected:
  - `ci:provider` - CI provider name
  - `ci:build_id` - CI build/pipeline ID
  - `ci:build_url` - CI build URL
  - Supports 5 CI providers: GitHub Actions, GitLab CI, Jenkins, Travis CI, CircleCI
- **Environment Variables** (env: prefix) - Auto-captured:
  - `env:GITHUB_SHA`, `env:GITHUB_REF`, `env:GITHUB_ACTOR` (GitHub Actions)
  - `env:CI_COMMIT_SHA`, `env:CI_PIPELINE_ID`, `env:CI_JOB_ID` (GitLab CI)
  - `env:GIT_COMMIT`, `env:BUILD_NUMBER`, `env:JOB_NAME` (Jenkins)
  - `env:TRAVIS_COMMIT`, `env:TRAVIS_BUILD_NUMBER` (Travis CI)
  - `env:CIRCLE_SHA1`, `env:CIRCLE_WORKFLOW_ID` (CircleCI)
  - User-requested env vars take precedence over auto-detected CI vars

### Improved
- **Security**: All metadata now cryptographically bound to test reports
- **Provenance**: Complete audit trail with signed metadata
- **Trust Model**: Environment metadata as trusted as user-provided metadata
- **Simplicity**: Single file per report (was: XML + JSON)
- **Compatibility**: Standard JUnit XML `<properties>` schema

### Removed
- JSON sidecar files for metadata (`metadata/{hash}.json`)
- `metadata/` storage directory
- Queue metadata JSON files (`queue/{hash}.json`)
- `storage.get_metadata()` method

### Documentation
- ADR-0011: Integrate Environment Metadata with pytest-metadata
- Sprint 7 plan: docs/sprints/sprint-07-metadata-integration.md
- Updated `docs/howto/add-metadata-to-reports.md` with git/CI/env metadata
- Complete rewrite of `docs/reference/api/metadata.md` (517 lines)
- All examples updated to reflect v0.3.0 implementation

### Tests
- 381 tests passing, 9 skipped, 16 xfailed
- 89.11% total coverage (metadata.py: 93.75%)
- 43 metadata tests (26 original + 17 new for git/CI/project name)
- New test classes: TestProjectNameCapture, TestGitMetadata, TestCIMetadata

## [0.2.1] - 2025-10-20

### Added
- **Sprint 6 (OpenSSF Best Practices Badge) - Complete**
- **SBOM Generation** (Software Bill of Materials):
  - Automated CycloneDX 1.6 JSON SBOM generation in build-release workflow
  - SBOM uploaded as release artifact for every release
  - SBOM validation job in security workflow
  - Comprehensive SBOM documentation (369 lines) in docs/security/SLSA_VERIFICATION.md
  - SBOM validation with cyclonedx-cli
  - SBOM-based dependency auditing with pip-audit
- **OpenSSF Best Practices Badge Readiness**:
  - Complete badge readiness assessment (342 lines) in docs/security/OPENSSF_BADGE_READINESS.md
  - 100% of MUST criteria documented and met
  - Evidence mapping for all badge requirements
  - Step-by-step badge application guide
- **Security Documentation**:
  - Root SECURITY.md file for GitHub Security tab integration
  - Updated docs/security/SECURITY.md with v0.2.0 status and current security practices
  - 48-hour response time, 90-day coordinated disclosure timeline
  - GitHub Security Advisories integration documented
- **Enhanced Dependency Scanning**:
  - pip-audit with --strict mode (fails CI on any vulnerabilities)
  - Trivy with exit-code enforcement (fails on critical/high vulnerabilities)
  - SBOM validation and dependency audit job in security workflow
- **Sprint 6 Retrospective**: Complete sprint analysis with metrics, learnings, and recommendations

### Changed
- **BREAKING CHANGE**: Config file location changed from ~/.jux/config to ~/.config/jux/config
  - Implements XDG Base Directory Specification compliance
  - Respects $XDG_CONFIG_HOME environment variable
  - Fallback to ~/.config/jux/config if XDG_CONFIG_HOME not set
  - Updated all documentation to reflect XDG-compliant paths
  - Updated tests to use new config path
  - No migration needed (alpha release, no installed base)
- Enhanced .github/workflows/security.yml with strict failure modes
- Updated codecov configuration with stricter thresholds (88% project target)

### Fixed
- Repository hygiene: Removed .jux-dogfood/jux.conf from git tracking (kept local file)
- XDG compliance: Config files now follow XDG Base Directory Specification
- Documentation consistency: All config file path references updated

### Security
- Strict dependency scanning prevents merging code with known vulnerabilities
- SBOM provides complete dependency transparency
- Enhanced supply chain security (SLSA L2 + SBOM + PyPI attestations + dependency scanning)

## [0.2.0] - 2025-10-20

### Added
- **Sprint 5 (Documentation & User Experience) - Complete**
- **Complete Diátaxis Documentation Framework** (50+ documents, 30,000+ lines):
  - **7 API Reference Pages** (auto-generated + enhanced):
    - canonicalizer.md (571 lines, hand-written with examples)
    - signer.md (685 lines, hand-written with examples)
    - verifier.md, storage.md, config.md, metadata.md, plugin.md (auto-generated + enhanced)
  - **3 Complete Tutorials** (beginner → intermediate → advanced):
    - First Signed Report (567 lines) - Beginner walkthrough with tamper detection
    - Integration Testing (extensive) - Multi-environment setup and CI/CD integration
    - Custom Signing Workflows (extensive) - Programmatic API usage and batch processing
  - **10 Comprehensive How-To Guides**:
    - Key Management: rotate-signing-keys.md (1,100+), secure-key-storage.md (1,200+), backup-restore-keys.md (1,100+)
    - Storage: migrate-storage-paths.md (1,000+), manage-report-cache.md (1,100+)
    - Configuration: multi-environment-config.md (766 lines, already existed)
    - Integration: integrate-pytest-plugins.md (1,100+), CI/CD deployment (existing)
    - Troubleshooting: troubleshooting.md (1,100+) - Comprehensive diagnostic guide
  - **4 Explanation Documents**:
    - Architecture (1,400+ lines) - System design, components, design decisions
    - Security (1,500+ lines) - Threat model, security best practices, compliance
    - Performance (1,400+ lines) - Benchmarks, scalability, optimization
    - Understanding pytest-jux (existing)
  - **Complete Reference Documentation**:
    - Configuration Reference (450+ lines) - All options with precedence rules
    - Error Code Reference (550+ lines) - Complete catalog with solutions
    - CLI Reference (sphinx-argparse-cli auto-generated for all 6 commands)
  - **Documentation Infrastructure**:
    - INDEX.md (650+ lines) - Complete documentation map with 50+ links
    - NAVIGATION.md (400+ lines) - Finding documentation by goal/topic
    - README.md updated with comprehensive documentation section

- **User Experience Improvements**:
  - **Enhanced CLI Help Text** (all 6 commands):
    - Rich descriptions with examples in epilog
    - Practical usage patterns
    - Cross-references to related commands
    - Better option descriptions
  - **Improved Error Messages** (errors.py module, 122 lines):
    - 23 error codes for programmatic handling
    - 13 specific error classes with actionable suggestions
    - User-friendly formatted output (no stack traces)
    - Debug mode support via JUX_DEBUG environment variable
  - **5 Configuration Templates**:
    - minimal - Basic options (10 lines)
    - full - All options with comments (45 lines)
    - development - Dev environment with RSA-2048 (25 lines)
    - ci - CI/CD with GitHub Actions/GitLab CI examples (50 lines)
    - production - Security requirements and RSA-4096 (60 lines)
  - **Shell Completion Scripts**:
    - completions/jux.bash (230 lines) - Bash completion
    - completions/jux.zsh (170 lines) - Zsh completion
    - completions/jux.fish (110 lines) - Fish completion
    - completions/README.md (280 lines) - Installation guide

- **Development Tools**:
  - **Quick-Start Script** (scripts/quickstart.sh, 300+ lines):
    - Interactive setup wizard with color-coded output
    - Key generation (RSA-2048, RSA-4096, ECDSA-P256)
    - Configuration creation from templates
    - Sample report generation, signing, and verification
    - Non-interactive mode (--non-interactive flag)
  - **Documentation Review Checklist** (.github/DOC_REVIEW_CHECKLIST.md, 650+ lines):
    - 10 major sections with detailed sub-checks
    - Diátaxis framework compliance
    - pytest-jux specific security checks
  - **Documentation Testing Script** (scripts/test_docs.py, 400+ lines):
    - Automatic code block extraction from Markdown
    - Bash and Python example validation
    - Color-coded test results
    - Dry-run and verbose modes

### Changed
- Sprint 5 target version updated from v0.3.0 to v0.2.0 (Sprint 4 postponed)
- Sphinx documentation infrastructure with autodoc and sphinx-argparse-cli
- All CLI commands refactored with create_parser() functions for autodoc
- README.md significantly expanded with documentation navigation

### Documentation
- **Time Saved**: ~5-7 days through Sphinx automation (autodoc + sphinx-argparse-cli)
- **Total Documents**: 50+ documents across all Diátaxis categories
- **Total Lines**: 30,000+ lines of documentation
- **Coverage**: 100% of planned Diátaxis categories populated

### Notes
- Sprint 5 completed in 1 day (2025-10-20) thanks to Sphinx automation
- All 6 epics complete (19 tasks total)
- Documentation framework now complete and production-ready
- Ready for v1.0.0 when Sprint 4 (API Integration) completes

## [0.1.9] - 2025-10-20

### Added
- REUSE/SPDX license identifiers in all source files
  - Machine-readable copyright: `SPDX-FileCopyrightText: 2025 Georges Martin`
  - Machine-readable license: `SPDX-License-Identifier: Apache-2.0`
  - ADR-0009 documenting REUSE/SPDX adoption
  - 372 lines of boilerplate removed (14 lines → 2 lines per file)
  - 31 Python files converted to REUSE format
  - Prepares for Sprint 6 SBOM generation with license compliance
- ADR-0010 documenting removal of unused database dependencies
- C4 DSL architecture model in `docs/architecture/workspace.dsl`
  - System context, container, and component views
  - Dynamic views for test execution and offline signing workflows
  - Validated with Structurizr CLI
  - Visualizable with Structurizr Lite

### Changed
- Copyright headers modernized from traditional Apache 2.0 format to REUSE/SPDX format
- All source files now use 2-line headers instead of 14-line headers
- **BREAKING**: Removed unused database dependencies (SQLAlchemy, Alembic, psycopg)
  - These were never used in pytest-jux (client-side plugin)
  - Database functionality resides in Jux API Server (separate project)
  - Reduces installation size by ~15MB
  - No functional impact (dependencies were not used)
  - ADR-0003 partially superseded by ADR-0010
- Renamed `codecov.yml` to `.codecov.yml` (dotfile convention)
- CLAUDE.md updated with foundational ADRs (ADR-0004, ADR-0005, ADR-0009, ADR-0010)
- ROADMAP.md updated to v0.1.8 status with recent improvements
- ADR-0003 marked as "Partially Superseded" (database sections only)

### Removed
- Obsolete initialization files: `init-git.sh`, `PROJECT_INIT_SUMMARY.md`, `QUICKSTART.md`, `SECURITY_FRAMEWORK_COMPLETE.md`
- Redundant `examples/` directory (documentation already covers examples)
- Moved dogfooding artifacts to `.jux-dogfood/` (DOGFOODING.md, dogfood-output.txt)

## [0.1.8] - 2025-10-19

### Fixed
- Build and Release workflow: Also exclude SLSA provenance file from PyPI upload

## [0.1.7] - 2025-10-19

### Fixed
- Build and Release workflow: Exclude checksums.txt from PyPI upload (fixes PyPI publish failure)

## [0.1.6] - 2025-10-19

### Fixed
- GitHub Actions CI/CD workflows (multiple improvements):
  - Plugin auto-enables when CLI options provided (fixes test failures)
  - Moved dogfooding config to `.jux-dogfood/` directory (isolated from CI)
  - Security scanning workflow adapted for private repositories
  - Replaced Safety scanner with pip-audit (no auth required)
  - Disabled OpenSSF Scorecard for private repos (API limitations)
  - Made Trivy SARIF upload non-blocking (Code Scanning requires GitHub Advanced Security)
  - Added `--no-cov` to security tests (placeholder stubs don't need coverage)

### Changed
- Security scanning tools updated:
  - Removed Safety CLI (now requires authentication)
  - Using pip-audit as primary dependency vulnerability scanner (official PyPA tool)
  - Trivy results now uploaded as artifacts for manual review

### Documentation
- Added comprehensive Gitflow release workflow documentation to CLAUDE.md
- Created release checklist template (.github/RELEASE_TEMPLATE.md)
- Documented Sprint 5 CI fixes in sprint-05-addendum-ci-fixes.md

## [0.1.5] - 2025-10-19

### Added
- Test coverage improvements to 91.92% (exceeds 92% target):
  - 8 new tests for exception handlers and error paths
  - commands/verify.py: 84.51% → 100% (+15.49%)
  - commands/inspect.py: 88.73% → 100% (+11.27%)
  - plugin.py: 91.74% → 97.25% (+5.51%)
  - signer.py: 89.09% → 92.73% (+3.64%)
- pytest-metadata integration for custom metadata in JUnit XML reports:
  - pytest-metadata>=3.0 added as required dependency
  - Automatic preservation of property tags during XMLDSig signing
  - Canonical hash computation includes property tags
  - Property tags preserved in stored reports (local and cache storage)
  - 6 comprehensive tests for metadata preservation, 100% passing
- Documentation for pytest-metadata integration:
  - docs/howto/add-metadata-to-reports.md (323 lines) - Complete guide for adding metadata
  - README.md updated with metadata support mention and examples

### Changed
- EnvironmentMetadata dataclass: Added pytest_jux_version field
- All existing tests updated to include pytest_jux_version in metadata constructions

### Tests
- Total: 346 passed, 9 skipped, 8 xfailed
- New exception handler tests:
  - test_verify.py: 3 tests for generic exception handling (JSON, quiet, normal output)
  - test_inspect.py: 2 tests for generic exception handling (JSON, normal output)
  - test_plugin.py: 4 tests for edge cases (config loading, missing files)
  - test_signer.py: 2 tests for exception handlers (sign/verify failures)

## [0.1.4] - 2025-10-18

### Added
- Comprehensive multi-environment configuration guide (Diátaxis how-to):
  - Configuration hierarchy and precedence documentation
  - Development, staging, and production deployment profiles
  - Platform-specific examples (GitHub Actions, GitLab CI/CD, Jenkins)
  - Key management strategies with Ansible deployment examples
  - Configuration validation and troubleshooting guide
  - Environment comparison matrix

### Changed
- CLAUDE.md development workflow updated to use `uv run` pattern:
  - All tool executions now use `uv run` (pytest, mypy, ruff)
  - Removed manual virtual environment activation steps
  - Simplified development commands for better developer experience
  - Updated development workflow, PR checklist, and security checklist

### Documentation
- docs/howto/multi-environment-config.md (766 lines) - Complete guide for dev/staging/prod configuration
- CLAUDE.md - Updated with uv best practices

## [0.1.3] - 2025-10-17

### Added
- Sprint 3 (Configuration, Storage & Caching) - Complete
- Configuration management module (`pytest_jux.config`):
  - Multi-source configuration (CLI, environment, files)
  - ConfigSchema with all configuration options
  - ConfigurationManager with load/validate/dump methods
  - Configuration precedence: CLI > env > files > defaults
  - Strict validation mode for dependency checking
  - 25 comprehensive tests, 85.05% code coverage
- Environment metadata module (`pytest_jux.metadata`):
  - EnvironmentMetadata dataclass for test context
  - capture_metadata() function for automatic collection
  - System information (hostname, username, platform)
  - Python and pytest version tracking
  - ISO 8601 timestamps with UTC timezone
  - Environment variable capture
  - 19 comprehensive tests, 92.98% code coverage
- Local storage & caching module (`pytest_jux.storage`):
  - XDG-compliant storage paths (macOS, Linux, Windows)
  - Four storage modes: LOCAL, API, BOTH, CACHE
  - ReportStorage class with atomic file writes
  - Offline queue for network-resilient operation
  - Secure file permissions (0600 on Unix)
  - get_default_storage_path() for platform detection
  - 33 comprehensive tests, 80.33% code coverage
- Cache management CLI command (`jux-cache`):
  - `jux-cache list`: List all cached reports
  - `jux-cache show`: Show report details by hash
  - `jux-cache stats`: View cache statistics
  - `jux-cache clean`: Remove old reports with dry-run mode
  - JSON output support for all subcommands
  - Custom storage path support
  - 16 comprehensive tests, 84.13% code coverage
- Configuration management CLI command (`jux-config`):
  - `jux-config list`: List all configuration options
  - `jux-config dump`: Show effective configuration with sources
  - `jux-config view`: View configuration files
  - `jux-config init`: Initialize configuration file (minimal/full templates)
  - `jux-config validate`: Validate configuration with strict mode
  - JSON output support for all subcommands
  - 25 comprehensive tests, 91.32% code coverage
- Documentation updates:
  - README.md: Added storage, caching, and configuration examples
  - CLAUDE.md: Updated with Sprint 3 architecture clarifications
  - Client-side only focus clearly documented

### Changed
- pyproject.toml: Added CLI entry points for `jux-cache` and `jux-config`
- Architecture documentation updated to clarify client-server separation
- Technology stack documentation updated (removed SQLAlchemy references)

### Postponed
- REST API client module (api_client.py) - Deferred until Jux API Server available
- Publishing commands - Dependent on API client implementation
- Plugin integration with storage - Deferred to Sprint 4

## [0.1.2] - 2025-10-15

### Added
- Sprint 2 (CLI Tools) - Complete
- Standalone CLI commands for offline operations:
  - `jux-keygen`: Cryptographic key pair generation
    - RSA key generation (2048, 3072, 4096 bits)
    - ECDSA key generation (P-256, P-384, P-521 curves)
    - X.509 self-signed certificate generation
    - Secure file permissions (0600 for private keys)
    - 31 comprehensive tests, 92.59% code coverage
  - `jux-sign`: Offline JUnit XML signing
    - Sign any JUnit XML file without pytest
    - Support for RSA and ECDSA keys
    - Optional X.509 certificate embedding
    - Stdin/stdout pipeline support
    - 18 comprehensive tests, 93.33% code coverage
  - `jux-verify`: XML signature verification
    - Verify XMLDSig signatures with certificates
    - Exit codes: 0 = valid, 1 = invalid
    - JSON output for scripting
    - Quiet mode option
    - 11 comprehensive tests, 78.48% code coverage
  - `jux-inspect`: JUnit XML report inspection
    - Display test summary (tests, failures, errors, skipped)
    - Show canonical SHA-256 hash
    - Detect signature presence
    - JSON output for scripting
    - Rich formatted terminal output
    - 9 comprehensive tests, 90.12% code coverage
- XML signature verification module (`pytest_jux.verifier`):
  - Verify XMLDSig signatures using signxml
  - Support for RSA and ECDSA signatures
  - Certificate validation
  - 6 comprehensive tests, 73.81% code coverage
- Configuration management:
  - configargparse for CLI with config file support
  - Environment variable support (JUX_KEY_PATH, JUX_CERT_PATH)
  - Config file support (~/.jux/config, /etc/jux/config)

### Changed
- Package management now uses `uv` (fast alternative to pip)
- Development documentation updated with uv usage
- CLI framework changed from click to configargparse for better config management

## [0.1.1] - 2025-10-15

### Added
- Sprint 1 (Core Plugin Infrastructure) - Complete
- XML canonicalization module (`pytest_jux.canonicalizer`):
  - C14N (Canonical XML) implementation for duplicate detection
  - SHA-256 canonical hash computation
  - Support for loading XML from files, strings, and bytes
  - 25 comprehensive tests, 82% code coverage
- XML digital signature module (`pytest_jux.signer`):
  - XMLDSig enveloped signature generation
  - RSA-SHA256 and ECDSA-SHA256 signature algorithms
  - Support for PEM-encoded RSA and ECDSA private keys
  - Optional X.509 certificate embedding
  - 28 comprehensive tests (21 passing, 7 xfail for self-signed cert limitations), 82% coverage
  - Test cryptographic keys (RSA 2048-bit, ECDSA P-256) for development
- pytest plugin hooks (`pytest_jux.plugin`):
  - `pytest_addoption`: CLI options (--jux-sign, --jux-key, --jux-cert)
  - `pytest_configure`: Configuration validation
  - `pytest_sessionfinish`: Automatic JUnit XML signing after test run
  - 21 comprehensive tests, 73% code coverage
  - End-to-end validated with actual pytest execution

### Security
- Test-only cryptographic keys clearly marked with security warnings
- Self-signed X.509 certificates for testing (not for production use)
- Comprehensive documentation on secure key management practices

## [0.1.0] - 2025-10-15

### Added
- Initial project structure following AI-Assisted Project Orchestration patterns
- Architecture Decision Records (ADRs):
  - ADR-0001: Record architecture decisions
  - ADR-0002: Adopt development best practices
  - ADR-0003: Use Python 3 with pytest, lxml, signxml, and SQLAlchemy stack
  - ADR-0004: Adopt Apache License 2.0
  - ADR-0005: Adopt Python Ecosystem Security Framework
- Apache License 2.0 with copyright attribution
- LICENSE and NOTICE files with proper copyright notices
- Comprehensive security framework:
  - Security documentation (SECURITY.md, THREAT_MODEL.md, CRYPTO_STANDARDS.md)
  - Automated security scanning (pip-audit, ruff security rules, safety, trivy)
  - GitHub Actions security workflow
  - Dependabot configuration
  - Pre-commit security hooks
  - OpenSSF Scorecard integration
  - Security test suite structure
- Diátaxis documentation framework structure
- C4 DSL architecture documentation structure
- Development environment configuration (.editorconfig, .pre-commit-config.yaml)
- Makefile with security targets
- Foundation for pytest plugin development
- Copyright headers in all source files

### Security
- Implemented Python ecosystem security framework (ADR-0005)
- STRIDE threat model with 19 identified threats
- Cryptographic standards documentation (NIST, RFC compliance)
- Vulnerability reporting process established
- Coordinated disclosure policy (90-day embargo)

[Unreleased]: https://github.com/jux-tools/pytest-jux/compare/v0.6.0...HEAD
[0.6.0]: https://github.com/jux-tools/pytest-jux/compare/v0.4.3...v0.6.0
[0.4.3]: https://github.com/jux-tools/pytest-jux/compare/v0.4.2...v0.4.3
[0.4.2]: https://github.com/jux-tools/pytest-jux/compare/v0.4.1...v0.4.2
[0.4.1]: https://github.com/jux-tools/pytest-jux/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/jux-tools/pytest-jux/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/jux-tools/pytest-jux/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/jux-tools/pytest-jux/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/jux-tools/pytest-jux/compare/v0.1.9...v0.2.0
[0.1.9]: https://github.com/jux-tools/pytest-jux/compare/v0.1.8...v0.1.9
[0.1.8]: https://github.com/jux-tools/pytest-jux/compare/v0.1.7...v0.1.8
[0.1.7]: https://github.com/jux-tools/pytest-jux/compare/v0.1.6...v0.1.7
[0.1.6]: https://github.com/jux-tools/pytest-jux/compare/v0.1.5...v0.1.6
[0.1.5]: https://github.com/jux-tools/pytest-jux/compare/v0.1.4...v0.1.5
[0.1.4]: https://github.com/jux-tools/pytest-jux/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/jux-tools/pytest-jux/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/jux-tools/pytest-jux/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/jux-tools/pytest-jux/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/jux-tools/pytest-jux/releases/tag/v0.1.0
