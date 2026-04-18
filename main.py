"""
OpenMEP — Open-source MEP Engineering Calculation Suite
Entry point: runs the FastAPI backend

Usage:
    python main.py                          # production
    uvicorn backend.main:app --reload       # development (with hot-reload)
    streamlit run streamlit_app/app.py      # Streamlit UI

GitHub: https://github.com/kakarot-oncloud/openmep
Author: Luquman A
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )
