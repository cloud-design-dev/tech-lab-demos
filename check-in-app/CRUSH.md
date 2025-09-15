# CRUSH.md - Check-in App Development Guide

## Build/Run Commands
- **Run locally**: `python app.py` (starts Flask dev server on port 8080)
- **Install deps**: `pip install -r requirements.txt`
- **Docker build**: `docker build -t checkin-app .`
- **Docker run**: `docker run -p 8080:8080 checkin-app`
- **Database init**: Database tables auto-created on first run via `ensure_database()`
- **Code Engine deploy**: `./code-engine/deploy.sh` (requires IBM Cloud CLI and env vars)

## Deployment Types
- **OpenShift**: Uses SQLAlchemy with PostgreSQL/SQLite, configured via DATABASE_URL
- **Code Engine**: Uses database.py with IBM Cloud PostgreSQL, configured via DATABASES_FOR_POSTGRESQL_CONNECTION
- **Local**: Uses SQLite fallback, no additional configuration needed

## Code Style Guidelines

### Python Style
- **Imports**: Standard library first, third-party, then local imports (separated by blank lines)
- **Functions**: Snake_case naming, descriptive names like `get_next_available_group()`
- **Classes**: PascalCase (User, Group, DatabaseOperations)
- **Constants**: UPPER_SNAKE_CASE (ADMIN_PASSWORD, IBM_SDK_AVAILABLE, CODE_ENGINE_DEPLOYMENT)
- **Variables**: Snake_case, descriptive (database_url, group_letter, vpc_number)

### Flask Patterns
- **Routes**: Use descriptive route names, group by functionality (/api/*, /admin/*)
- **Error handling**: Try/catch with db.session.rollback() on exceptions (SQLAlchemy only)
- **JSON responses**: Always include success/error status and descriptive messages
- **Database**: Use SQLAlchemy ORM for OpenShift, database.py operations for Code Engine
- **Environment**: Use os.environ.get() with sensible defaults
- **Deployment detection**: Check CODE_ENGINE_DEPLOYMENT flag for conditional logic

### Database Conventions
- **Models**: Include to_dict() methods for JSON serialization (SQLAlchemy only)
- **Queries**: Use descriptive variable names, handle None cases
- **Transactions**: Explicit commit/rollback for SQLAlchemy, automatic for database.py
- **Dual support**: Functions must handle both SQLAlchemy objects and dict responses

### Security
- **Secrets**: All sensitive data via environment variables
- **Validation**: Validate all user inputs, normalize emails to lowercase
- **Authentication**: Session-based admin auth, password comparison
- **Database**: Use parameterized queries, never string concatenation