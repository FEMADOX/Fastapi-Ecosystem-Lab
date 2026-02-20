# fastapi-new — Official FastAPI Project Template

> Source: <https://github.com/fastapi/fastapi-new>

Create a new FastAPI project in one command. ✨

---

## How to use

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) following their guide for your system.

Run:

```sh
uvx fastapi-new awesomeapp
```

This creates a new project `awesomeapp` with a basic FastAPI app, configured with `uv`.

Enter the directory:

```sh
cd awesomeapp
```

Run the development server:

```sh
uv run fastapi dev
```

Open your browser at `http://localhost:8000` to see your new FastAPI app running!

---

## Existing directory

If you want to create a new FastAPI project in an **existing** directory, run without a project name:

```sh
uvx fastapi-new
```

---

## Generated project structure

```text
awesomeapp/
├── src/
│   └── awesomeapp/
│       └── main.py
├── tests/
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── pyproject.toml
└── uv.lock
```

### Key points from the template

- Uses `src/` layout (avoids accidental imports without installing the package)
- Uses `uv` as package manager
- Includes `tests/` from the start
- Includes `ruff` via `.pre-commit-config.yaml` for linting/formatting
- `.python-version` pins the Python version

---

## Notes

- This is the **official** template maintained by the FastAPI team (tiangolo)
- It is intentionally minimal — it gives you the skeleton, not a full app
- Combine it with the patterns from `fastapi-best-practices` for production use
