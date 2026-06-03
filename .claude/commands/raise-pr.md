Follow these steps in order. Do not skip a step.

1. Run the full test suite with coverage:
   uv run pytest --cov=app --cov-report=term-missing -v

2. Check the coverage percentage reported for the `app` package.
   - If total coverage is below 80%, identify the specific uncovered lines from the `term-missing` output.
   - Write additional tests in `tests/test_deployments.py` to cover those lines, then re-run step 1.
   - Repeat until coverage is ≥ 80%.

3. Display the final coverage report to the user and confirm coverage is ≥ 80% before continuing.

4. Run the linter to catch any issues before committing:
   uv run ruff check . && uv run ruff format --check .

5. Stage all modified and new files. Do NOT stage `.env` or `*.db` files.

6. Check `git log --oneline -5` to understand the commit message style used in this repo.

7. Write a commit message that:
   - Summarises what changed (new feature, bug fix, refactor, tests, etc.)
   - Mentions the coverage achieved (e.g. "test coverage at 85%")
   - Ends with: Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

8. Commit the changes.

9. Push the branch to origin.

10. Create a pull request with:
    gh pr create --title "<concise title>" --body "..."
    The PR body must include: a Summary section, the coverage percentage, and a Test plan checklist.
