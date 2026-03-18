# Sample AGENTS.md file

## Dev environment tips

- Run `uv add <package_name>` to add the package to your workspace.
- After moving files or changing imports, run `ruff check <project_name>` to be sure Python linting rules still pass.
- Use `ruff check --fix <project_name>` to automatically fix linting issues.
- Use `ruff format --check <project_name>` to check for formatting issues and `ruff format --fix <project_name>` to automatically fix them.
- Use `ty check <project_name>` to check for type errors.
- Use `ty explain <rule_name>` to get an explanation of a specific linting rule.

## Testing instructions

- Find the CI plan in the .github/workflows folder.
- Run `pytest` to run every check defined for that package.
- From the package root you can just call `pytest`. The commit should pass all tests before you merge.
- To focus on one step, add the pytest pattern: `pytest -k "<test name>"`.
- To run a specific test file: `pytest <path_to_test_file>`.
- To run a specific test function: `pytest <path_to_test_file>::<test_class_name>::<test_function_name>`.
- To run tests with a specific marker: `pytest -m <marker_name>`.
- To run tests in parallel: `pytest -n <number_of_processes>` or use `pytest -n auto` to automatically detect the number of available CPUs.
- Fix any test or type errors until the whole suite is green.
- Add or update tests for the code you change, even if nobody asked.

## PR instructions

- Title format: [<project_name>] [<the_title>]
- Always run `ruff check`, `ruff format --check`, and `pytest` before committing.
