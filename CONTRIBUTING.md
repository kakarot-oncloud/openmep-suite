# Contributing to OpenMEP

Thank you for considering a contribution to OpenMEP. Every improvement — from a typo fix to a new calculation engine — matters.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Project Structure](#project-structure)
4. [Development Workflow](#development-workflow)
5. [Types of Contributions](#types-of-contributions)
6. [Code Style](#code-style)
7. [Testing](#testing)
8. [Pull Request Process](#pull-request-process)
9. [Contribution Recognition](#contribution-recognition)

---

## Code of Conduct

By participating in this project, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md). Please be respectful and professional — this is an engineering tool that engineers trust.

---

## Getting Started

```bash
git clone https://github.com/kakarot-oncloud/openmep-suite.git
cd openmep
pip install -r requirements.txt -r requirements-dev.txt

# Verify the backend starts cleanly
uvicorn backend.main:app --reload --port 8000

# Run all tests (path is configured in pyproject.toml)
pytest -v
```

---

## Project Structure

```
backend/
├── engines/         # Pure calculation functions — no FastAPI, no I/O
├── api/routes/      # FastAPI routers — thin layer that calls engines
├── models/          # Pydantic request/response models
└── main.py          # App factory, router registration
streamlit_app/
├── app.py           # Home page + sidebar nav
├── utils.py         # Shared: region selector, API client, UI helpers
└── pages/           # One file per calculator page (numbered 1–26)
docs/                # All documentation
backend/tests/       # Pytest test suite
src/
├── engines/         # TypeScript: compliance-guardian, pdf-generator, submission-service
├── lib/             # TypeScript: project-store, version-store, branding-store
└── routes/          # TypeScript: REST handlers for /api/projects, /api/submission
```

> **Note on `src/`:** This is the Node.js/Express Project Management API layer — not a React frontend. It handles project workspaces, version history, submission packaging, and company branding. See [`src/README.md`](src/README.md) for details.

---

## Development Workflow

1. **Fork** the repository and create a feature branch:
   ```bash
   git checkout -b feature/australia-cable-correction
   ```

2. **Make changes.** If adding a calculator, follow [ADDING_NEW_CALCULATOR.md](docs/contributing/ADDING_NEW_CALCULATOR.md).

3. **Write or update tests** in `backend/tests/`.

4. **Run the full test suite:**
   ```bash
   pytest backend/tests/ -v --tb=short
   ```

5. **Check linting:**
   ```bash
   ruff check backend/ streamlit_app/
   ```

6. **Check for regressions** — all existing tests must pass.

7. **Commit with a descriptive message:**
   ```
   feat(electrical): add harmonic derating for AS/NZS 3008 Table 27
   ```

8. **Push and open a PR** against `main`.

> **Tip — pre-commit hooks (recommended):** Install `pre-commit` to run linting and formatting checks automatically on every commit before it reaches CI:
> ```bash
> pip install pre-commit
> pre-commit install
> ```
> After `pre-commit install`, running `git commit` will automatically run `ruff check`, `ruff-format`, and file hygiene checks. Fix any failures, then re-commit. Run `pre-commit run --all-files` to check the whole codebase at any time.

---

## Types of Contributions

### Bug Fixes
- Open an issue first if the bug is non-trivial
- Reference the issue number in your PR

### New Calculation Modules
- Follow the engine adapter pattern (see [ADDING_NEW_CALCULATOR.md](docs/contributing/ADDING_NEW_CALCULATOR.md))
- One engine file, one route handler, one Streamlit page
- Must include at least 2 tests with known-good reference values from the applicable standard

### New Regions
- Follow [ADDING_NEW_REGION.md](docs/contributing/ADDING_NEW_REGION.md)
- Provide a source reference for every design condition or correction factor

### Documentation
- Typo fixes and clarifications are always welcome
- Follow the existing style and tone

---

## Code Style

- Python: formatted with **ruff** (`ruff check` runs in CI)
- Commit messages: follow [Conventional Commits](https://www.conventionalcommits.org/) — `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
- No magic numbers — constants must be named and cited to the applicable standard clause
- Engine functions must be pure (no I/O, no side effects)

---

## Testing

All tests live in `backend/tests/`. To run:

```bash
# Run all tests (path configured in pyproject.toml)
pytest -v

# With coverage
pytest --cov=backend --cov-report=term-missing

# Run a specific file
pytest backend/tests/test_cable_sizing.py -v
```

Every new calculation module must include:
- At least 2 tests with reference values traceable to the applicable standard
- At least 1 test per supported region
- Edge case tests (zero load, maximum load, boundary conditions)

---

## Pull Request Process

1. Ensure all tests pass and linting is clean
2. Update the relevant documentation in `docs/` if behaviour changed
3. Fill in the PR template — module name, standard referenced, test coverage
4. A maintainer will review within a few days
5. After approval and merge, your contribution will appear in the next release

---

## Contribution Recognition

All contributors are listed in the project's [GitHub contributors graph](https://github.com/kakarot-oncloud/openmep-suite/graphs/contributors). Significant contributions (new modules, new regions) are called out in the release notes.
