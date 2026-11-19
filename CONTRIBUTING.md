# Contributing to ScamRoad

Thank you for your interest in contributing to ScamRoad! This guide outlines the development process and standards for submitting improvements.

---

## Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Priya-Ranjan-0201/potholes-detection.git
cd potholes-detection
```

### 2. Backend Environment
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r backend/requirements.txt
```

### 3. Frontend Environment
```bash
cd web
npm install
cd ..
```

---

## Code Quality & Standards

- **Python**: Follow PEP 8 style guidelines. Code is formatted with `black` and linted with `ruff`.
- **TypeScript & React**: Follow standard ESLint and TypeScript strict typing rules.
- **Git Commits**: Use conventional commits (e.g., `feat:`, `fix:`, `docs:`, `chore:`).

---

## Running Verification Tests

Before opening a pull request, ensure all test suites pass cleanly:

```bash
# 1. Run backend tests (95 tests)
pytest backend/tests

# 2. Run machine learning acceptance benchmarks
python ml2/tests/test_acceptance.py --pipeline ml2 --test a1

# 3. Run frontend unit tests
cd web && npm test -- --run

# 4. Verify frontend production build
cd web && npm run build
```

---

## Submitting Pull Requests

1. Fork the repository and create your feature branch: `git checkout -b feat/my-improvement`.
2. Commit your changes with clear, descriptive commit messages.
3. Push to your fork: `git push origin feat/my-improvement`.
4. Open a Pull Request against the `main` branch with the provided PR template.
