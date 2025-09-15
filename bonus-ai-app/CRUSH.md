# CRUSH Configuration for OpenShift Demo Lab Applications

## Build/Test/Lint Commands
```bash
# Development server (Flask apps)
python app.py                    # Run development server
mise run v1-dev                  # Run V1 demo app locally
mise run v2-dev                  # Run V2 demo app locally
mise run checkin-dev             # Run check-in app locally

# Docker operations
mise run v1-docker-build         # Build V1 Docker image
mise run v1-docker-run           # Run V1 with resource limits
mise run v2-docker-build         # Build V2 Docker image
mise run clean-docker            # Stop all demo containers

# Testing (basic - no formal test suite)
python -c "from app import app; print('✓ App imports successfully')"

# Dependencies
pip install -r requirements.txt  # Install Python dependencies
mise run install-all            # Install all app dependencies
```

## Code Style Guidelines
- **Language**: Python 3.12 with Flask framework
- **Imports**: Standard library first, third-party, then local imports
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Error Handling**: Try/except blocks with graceful fallbacks (see psutil import pattern)
- **Environment**: Use os.environ.get() with defaults for configuration
- **Database**: SQLAlchemy ORM with PostgreSQL (production) / SQLite (local)
- **Templates**: Jinja2 templates in templates/ directory
- **Static Files**: CSS/JS in static/ directory
- **Comments**: Docstrings for functions, inline comments for complex logic
- **Global State**: Use app-level dictionaries for request tracking/stats