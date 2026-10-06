---
name: python-package-fix-workflow
description: Use when fixing bugs in a Python package that requires regression tests and changelog updates.
---
1. Inspect the package structure and existing test conventions before editing.
2. Add type annotations to every parameter and return value of every public function in the package; exclude names starting with `_`.
3. Add `tests/test_regressions.py` with one passing test function per fixed bug, and include at least 3 test functions.
4. Record each fix in `CHANGELOG.md` under `## Unreleased` using the exact bullet format `- fix(<function name>): <short description>`.
5. Run the test suite from the project root so package imports resolve correctly; fix failures before finishing.
6. Self-check: public annotations complete; regression tests pass; changelog has the required heading and bullets.
