# GitHub Copilot Commit Message Guidelines

When generating or proposing git commit messages for this project, always adhere to the **Conventional Commits** specification.

## Commit Message Structure
```text
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

## Guidelines
- **Type**: Must be one of the following:
  - `feat`: A new feature
  - `fix`: A bug fix
  - `docs`: Documentation only changes
  - `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
  - `refactor`: A code change that neither fixes a bug nor adds a feature
  - `perf`: A code change that improves performance
  - `test`: Adding missing tests or correcting existing tests
  - `build`: Changes that affect the build system or external dependencies (example scopes: pip, poetry, uv, npm)
  - `ci`: Changes to our CI configuration files and scripts (example scopes: GitHub Actions)
  - `chore`: Other changes that don't modify src or test files
  - `revert`: Reverts a previous commit

- **Scope**: Use a scope that identifies the module or area of the codebase being changed (e.g., `auth`, `users`, `items`, `exceptions`, `pre-commit`).
- **Subject (Description)**:
  - Use the imperative, present tense: "change" not "changed" nor "changes".
  - Don't capitalize the first letter.
  - No dot (.) at the end.
- **Body**:
  - Explain **what** and **why** vs. how.
  - Wrap lines at approximately 72 characters.
- **Footer**: Reference issues or PRs (e.g., `Refs: #123` or `Closes: #456`).

## Examples
- `feat(auth): add JWT token refresh endpoint`
- `fix(items): prevent duplicate item names for the same user`
- `refactor(exceptions): convert singletons to factory functions`
- `docs(readme): update installation instructions for Windows`
