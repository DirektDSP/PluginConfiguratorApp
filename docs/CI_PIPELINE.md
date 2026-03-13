# CI Pipeline Documentation

## Overview

The CI pipeline is designed to be **smart and efficient** - it only runs the necessary checks based on what files have been changed.

## Workflow Files

### 1. `ci.yml` - Main CI Pipeline

The main workflow that runs on every push and pull request to `main` or `develop` branches.

### 2. `pr-checks.yml` - Pull Request Specific Checks

Additional checks that run only on PRs, including:
- PR summary generation
- Label validation
- Merge conflict detection

### 3. `update-status.yml` - Status Badge Updates

Updates CI status badges automatically (optional).

## Smart Job Execution

The CI pipeline uses the `dorny/paths-filter` action to detect which files changed and only runs relevant jobs:

| File Type Change      | Jobs Run                                           |
|----------------------|----------------------------------------------------|
| Python files (`*.py`) | lint, typecheck, test                             |
| Test files (`tests/`) | test                                               |
| Docs (`*.md`, `docs/`) | markdown-lint                                     |
| Dependencies (`pyproject.toml`, `uv.lock`) | security, all jobs          |
| Other files          | No jobs (validation only)                          |

## Job Descriptions

### `detect-changes`
**Always runs first.** Analyzes the commit to determine which files changed and sets outputs for downstream jobs.

### `lint`
**Runs when Python files change.** Performs code quality checks:
- **ruff check** - Fast Python linter (100+ rules)
- **ruff format** - Code formatting check
- **isort** - Import sorting check

### `typecheck`
**Runs when Python files change.** Performs static type checking:
- **mypy** - Python type checker with strict optional checking

### `test`
**Runs when Python or test files change.** Executes the test suite:
- Runs on Python 3.12 and 3.13
- Generates coverage reports (XML, HTML, terminal)
- Uploads coverage to Codecov
- Archives HTML test reports as artifacts

### `security`
**Runs when dependency files change.** Security auditing:
- **safety** - Checks for known security vulnerabilities
- **pip-audit** - Additional dependency auditing

### `markdown-lint`
**Runs when documentation files change.** Validates Markdown formatting:
- Uses markdownlint-cli2
- Configured in `.markdownlint.json`

### `integrity-check`
**Always runs after all required jobs.** Verifies CI pipeline integrity and provides status.

## Configuration Files

### `ruff.toml`
Comprehensive ruff configuration with:
- 100+ linting rules enabled
- Line length: 100 characters
- Per-file ignoring for tests and UI files
- Import sorting configuration

### `pyproject.toml`
Contains:
- `tool.isort` - Import sorting configuration
- `tool.mypy` - Type checking configuration
- `tool.coverage.*` - Coverage reporting configuration
- `tool.pytest.ini_options` - Test runner configuration

### `.markdownlint.json`
Markdown linting rules:
- Line length: 120 characters
- Allows HTML elements (br, div, span, img)
- Ignores first-level heading duplication
- Ignores emphasis style rules

## Local Development

### Pre-commit Hooks

Install pre-commit hooks to catch issues locally:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files

# Run on changed files only
pre-commit run
```

### Running Checks Manually

```bash
# Install dependencies
uv sync

# Install dev tools
uv add --dev ruff black isort mypy pytest pytest-qt

# Run linting
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run isort --check-only src/ tests/

# Run type checking
uv run mypy src/ --ignore-missing-imports

# Run tests
uv run pytest tests/ --cov=src --cov-report=html

# Run security audit
uv add --dev safety
uv run safety check
```

## Best Practices

### 1. Follow the Path-Based Rules

The CI will only run jobs relevant to your changes. This saves time and resources.

### 2. Use Pre-commit Locally

Most CI failures can be caught before pushing by running pre-commit hooks.

### 3. Separate Your Changes

If you're making both code and documentation changes, consider splitting them into separate commits or PRs. This allows the CI to run only the relevant checks.

### 4. Monitor Coverage

Coverage reports are uploaded to Codecov and available in the HTML report artifacts. Aim for >80% coverage on new code.

### 5. Fix Security Issues Promptly

Security audit failures are treated as critical. Address these immediately.

## CI/CD Pipeline Flow

```
push/PR to main/develop
         ↓
   detect-changes
         ↓
   ┌──────┴──────┐
   ↓             ↓
Python?      Tests?   Docs?   Deps?
   ↓             ↓       ↓       ↓
lint          test   markdown   security
typecheck
   ↓
   └──────┴──────┐
                  ↓
           integrity-check
                  ↓
              CI Complete
```

## Troubleshooting

### CI Fails on Linting

```bash
# Auto-fix linting issues
uv run ruff check --fix src/ tests/
uv run ruff format src/ tests/
uv run isort src/ tests/
```

### CI Fails on Type Checking

```bash
# Check type errors
uv run mypy src/ --ignore-missing-imports --show-error-codes

# Add type hints to fix errors
```

### CI Fails on Tests

```bash
# Run tests locally with verbose output
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_base_tab.py -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html
```

### CI Fails on Markdown Linting

```bash
# Run markdownlint
npx markdownlint-cli2 "**/*.md" --config .markdownlint.json

# Auto-fix (limited)
npx markdownlint-cli2 "**/*.md" --fix
```

## Artifacts

After each test run, the following artifacts are available for download:

1. **Test Reports** (`pytest-report.html`) - Detailed HTML test report
2. **Coverage Reports** (`htmlcov/`) - Interactive coverage report

These are retained for 30 days.

## Status Indicators

- ✅ **All checks passing** - Ready to merge
- ⚠️ **Non-critical failure** - Review and fix
- ❌ **Critical failure** - Must fix before merge

## Next Steps

1. Install pre-commit hooks locally
2. Run `pre-commit run --all-files` to verify setup
3. Push a small change to trigger the CI pipeline
4. Monitor the first CI run for any issues
5. Add coverage badge to README (optional)