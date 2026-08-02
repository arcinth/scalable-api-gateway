# Contributing

## Setup

```bash
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows

pip install -r requirements-dev.txt
pre-commit install
```

`pre-commit install` runs isort, Black, and Ruff on `git commit`. To run
them manually:

```bash
isort .
black .
ruff check .
pytest
```

## Standards

- **Formatting**: [Black](https://github.com/psf/black), line length 88.
- **Imports**: [isort](https://pycqa.github.io/isort/), Black-compatible profile.
- **Linting**: [Ruff](https://docs.astral.sh/ruff/) — `ruff check .` runs in CI.
- **Tests**: [pytest](https://docs.pytest.org/), under `tests/`.

## Branching & commits

- Branch from `main`, e.g. `fix/rate-limit-ip`.
- Keep commits scoped to one logical change.
- Open a PR against `main`; CI (Ruff, Black check, isort check, pytest)
  must pass before merge.
- If a change alters request/response behavior (auth, routing, caching,
  rate limiting), say so explicitly in the PR description.

## Questions

[TODO: add a discussion/issue link once the project has a public home
for questions.]
