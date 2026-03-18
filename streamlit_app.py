"""Entry point for Streamlit Community Cloud deployment.

Streamlit Community Cloud looks for a file named ``streamlit_app.py`` at the
repository root.  This file delegates to the main Streamlit application defined
in ``learn_streamlit/src/app.py`` so the cloud runner can find it without
changing the project structure.

Local usage:
    uv run streamlit run streamlit_app.py

Streamlit Community Cloud usage:
    - Repository: FEMADOX/Fastapi-Ecosystem-Lab
    - Main file path: streamlit_app.py
    - Set the FastAPI backend URL via Streamlit Secrets:
        [env]
        FASTAPI_BASE_URL = "https://<your-fastapi-deployment>.example.com/api/v1"

Implementation note:
    Streamlit re-runs the entire script file on every widget interaction.
    A plain ``from ... import *`` would not re-call ``render()`` on subsequent
    re-runs because Python caches imported modules.  Using ``importlib.reload``
    forces the module (and therefore ``render()``) to be re-executed on each
    Streamlit re-run, just as it would be if Streamlit were running
    ``learn_streamlit/src/app.py`` directly.
"""

import importlib
import sys

_APP_MODULE = "learn_streamlit.src.app"

# Reload the app module on every Streamlit re-run so the UI is rebuilt
# correctly; first-time import executes the module (and render()) normally.
if _APP_MODULE in sys.modules:
    importlib.reload(sys.modules[_APP_MODULE])
else:
    import learn_streamlit.src.app  # noqa: F401
