# OpenShift Demo Lab Applications

This repository contains three demonstration applications designed for OpenShift and container orchestration technical labs.

## Applications Overview

### Demo App V1 (`demo-app-v1/`)
A Flask-based web application that demonstrates **ephemeral storage** characteristics in containerized environments.

**Key Features:**
- In-memory data persistence (lost on restart)
- Real-time container resource monitoring (CPU/RAM usage)
- Traffic generation endpoints for scaling demonstrations
- Step-by-step progress visualization
- "Reload Page" functionality to demonstrate data loss

**Purpose:** Shows the limitations of in-memory storage and the need for persistent solutions.

### Demo App V2 (`demo-app-v2/`)
An enhanced Flask application that demonstrates **persistent storage** using database backends.

**Key Features:**
- PostgreSQL/SQLite database persistence (survives restarts)
- Advanced step progression with manual completion controls
- Enhanced container resource monitoring with limits detection
- Database debug endpoints and persistence statistics
- Automatic database initialization and connection handling

**Purpose:** Demonstrates how persistent storage solves container data challenges and enables production deployments.

### Check-in App (`check-in-app/`)
A registration system for lab participants with automated group assignment.

**Key Features:**
- Email-based user registration with validation
- Automatic group assignment (3 users per group)
- Admin dashboard showing all participants
- IBM Cloud SDK integration for user validation
- Real-time registration statistics

**Purpose:** Manages participant registration and group organization for hands-on lab sessions.

## Architecture Comparison

| Feature | V1 (Ephemeral) | V2 (Persistent) |
|---------|----------------|-----------------|
| Storage | In-memory | PostgreSQL/SQLite |
| Data Survival | ❌ Lost on restart | ✅ Survives restarts |
| Resource Monitoring | ✅ CPU/RAM metrics | ✅ Enhanced metrics |
| Production Ready | Basic demo | Full production |

## Development

The repository includes automated task management via `mise.toml` for streamlined development workflows:

```bash
# V1 Development
mise run v1-dev

# V2 Development  
mise run v2-dev

# Check-in App Development
mise run checkin-dev
```

## Deployment

All applications include OpenShift deployment manifests with:
- Resource limits and health checks
- BuildConfig for S2I deployments
- Secure HTTPS routes with TLS termination
- Horizontal scaling capabilities

Perfect for demonstrating container orchestration concepts, storage persistence, resource management, and production deployment patterns in OpenShift environments.
