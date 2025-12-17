# Prompt Manager - Project Structure

## Core Application Files
- `app.py` - Main Flask web application (primary entry point)
- `prompt_manager.py` - Core prompt management logic
- `keyboard_listener.py` - Global keyboard monitoring and text expansion
- `gemini_client.py` - Gemini AI integration for prompt enhancement
- `prompts.json` - Default prompts storage

## Alternative Entry Points
- `gui.py` - Desktop GUI application (CustomTkinter)
- `background_service.py` - Background service with system tray icon
- `service_manager.py` - Service management utilities (used by gui.py)
- `setup_startup.py` - Windows startup configuration script

## Web Application
### Templates (`templates/`)
- `add.html` - Add new prompt page (home route `/`)
- `existing.html` - Existing prompts management page (`/existing`)
- `index.html` - Home page with recently used prompts
- `landing.html` - Landing page (`/landing`)

### Static Files (`static/`)
- `style.css` - Main stylesheet (dark theme, Manrope font)
- `common.js` - Shared JavaScript functions
- `landing.css` - Landing page styles
- `manifest.json` - PWA manifest
- `sw.js` - Service worker (currently not registered, kept for future use)

## Configuration & Documentation
- `requirements.txt` - Python dependencies
- `README.md` - Project documentation
- `run.bat` - Windows batch script for server control
- `.gitignore` - Git ignore rules

## Ignored Files (Local Development)
- `__pycache__/` - Python cache files (auto-generated)
- `verify_changes.py` - Local test script
- `verify_enhancement.py` - Local test script
- `.env` - Environment variables (API keys)

## Usage
- **Web App**: `python app.py` (runs on http://localhost:5000)
- **GUI App**: `python gui.py`
- **Background Service**: `python background_service.py`
- **Server Control**: Use `run.bat` for start/restart/stop

