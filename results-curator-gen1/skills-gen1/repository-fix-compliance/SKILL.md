---
name: repository-fix-compliance
description: Use when fixing bugs in a code repository with required typing, regression-test, and changelog conventions.
---
1. Inspect the package, existing tests, and project instructions before editing.
2. Add type annotations for every parameter and return value of every public function you add or modify.
3. Add one regression test per fixed bug in `tests/test_regressions.py`; meet any stated minimum test count.
4. Record each fix under `## Unreleased` in `CHANGELOG.md` using `- fix(<function name>): <short description>`.
5. Run tests from the project root so package imports resolve; investigate collection errors instead of treating them as passing tests.
6. Run the full test suite after the changes and confirm the changelog and regression tests are present.
7. Self-check: public annotations complete; regressions cover each fix; changelog entries follow the required format; tests pass.
