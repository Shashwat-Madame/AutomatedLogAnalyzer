# Automated Log File Analyzer

A beginner-friendly Python mini-project that reads `.log` and `.txt` files, identifies log levels, summarizes issue frequency, visualizes results, and exports CSV/TXT reports.

## Requirements
- Python 3.10 or newer
- Internet connection for the initial package installation

## Run on Windows (VS Code / PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If PowerShell blocks virtual environment activation, run this for the current terminal session and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Open the local URL shown in the terminal, usually `http://localhost:8501`.

## Features
- Load the included sample log or upload a `.log` / `.txt` file
- Detect CRITICAL, ERROR, WARNING, INFO, DEBUG and unrecognized entries
- Summarize counts and severity
- View Plotly charts and repeated issues
- Search/filter detailed entries
- Download CSV and text reports

## Project files
- `app.py`: Streamlit dashboard
- `analyzer.py`: parsing and report logic
- `sample.log`: test data
- `requirements.txt`: required packages

This is a keyword-based educational analyzer, not a full OS-specific log parser or an automatic root-cause diagnostic tool.
