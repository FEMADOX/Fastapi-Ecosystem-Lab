"""Launcher for the Streamlit frontend."""

import sys
from pathlib import Path

from streamlit.web import cli as stcli


def main() -> None:
    """Run the Streamlit server for the frontend app."""
    app_path = Path(__file__).with_name("app.py")
    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--server.fileWatcherType=poll",
    ]
    raise SystemExit(stcli.main())


if __name__ == "__main__":
    main()
