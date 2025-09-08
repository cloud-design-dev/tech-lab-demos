# OpenShift Demo Lab Applications

This repository contains a comprehensive suite of demonstration applications designed for OpenShift and container orchestration technical labs. The demo applications progress from basic containerization concepts through advanced production-ready deployments.

## Demo Application Progression

This lab follows a progressive approach to demonstrate increasingly sophisticated OpenShift concepts:

### Demo App V1: Ephemeral Storage (`demo-app-v1/`)
**Focus:** Basic containerization and ephemeral storage limitations

A Flask-based web application demonstrating **ephemeral storage** characteristics in containerized environments.

**Key Concepts:**
- In-memory data persistence (lost on restart)
- Real-time container resource monitoring (CPU/RAM usage vs limits)
- Basic OpenShift deployment patterns
- Step-by-step progress visualization
- Data loss demonstration via "Reload Page" functionality

**Learning Outcomes:** Understanding container storage limitations and the need for persistent solutions.

### Demo App V2: Persistent Storage (`demo-app-v2/`)
**Focus:** Database persistence and production deployment patterns

An enhanced Flask application demonstrating **persistent storage** using database backends.

**Key Concepts:**
- PostgreSQL database persistence (survives pod restarts and scaling)
- Advanced step progression with manual completion controls
- Enhanced container resource monitoring with deployment limits
- Database connection handling and initialization
- Production-ready deployment manifests

**Learning Outcomes:** How persistent storage enables stateful applications and production deployments.

### Demo App V3: Resource Management & Auto-Scaling (`demo-app-v3/`)
**Focus:** OpenShift CLI operations, resource limits, and horizontal scaling

CLI-focused deployment demonstrating **resource management** and **horizontal pod autoscaling**.

**Key Concepts:**
- Aggressive resource limits for scaling demonstrations
- Horizontal Pod Autoscaler (HPA) configuration
- Built-in load testing to trigger scaling events
- Real-time resource monitoring (CPU/memory vs limits)
- `oc` command-line deployment workflows

**Learning Outcomes:** Production resource management, autoscaling behavior, and CLI-driven operations.

### Demo App V4: Health Probes & Application Readiness (`demo-app-v4/`)
**Focus:** Application lifecycle management and health probe configuration

Advanced deployment workflow demonstrating **health probe configuration** and **production readiness**.

**Key Concepts:**
- Health probe detection and status monitoring (liveness, readiness, startup)
- Step 6 completion workflow based on probe configuration
- Multiple probe configuration methods (YAML files, CLI patches)
- Application lifecycle management and self-healing containers
- Production health monitoring and troubleshooting

**Learning Outcomes:** Complete application lifecycle management from deployment through production monitoring.

### Check-in App: Lab Registration System (`check-in-app/`)
**Focus:** Lab participant management and group organization

A registration system for lab participants with automated group assignment and admin controls.

**Key Features:**
- Email-based user registration with IBM Cloud SDK validation
- Automatic group assignment (3 users per group)
- Admin dashboard with password protection
- Real-time registration statistics and completion tracking
- PostgreSQL integration with OpenShift deployment

**Purpose:** Manages participant registration and group organization for hands-on lab sessions.

## Architecture Comparison

| Feature | V1 (Ephemeral) | V2 (Persistent) | V3 (Resource Mgmt) | V4 (Health Probes) |
|---------|----------------|-----------------|-------------------|-------------------|
| **Storage** | In-memory | PostgreSQL/SQLite | PostgreSQL | PostgreSQL |
| **Data Survival** | ❌ Lost on restart | ✅ Survives restarts | ✅ Survives restarts | ✅ Survives restarts |
| **Resource Monitoring** | ✅ CPU/RAM metrics | ✅ Enhanced metrics | ✅ Limits vs usage | ✅ Container-aware |
| **Auto-Scaling** | ❌ Manual scaling | ❌ Manual scaling | ✅ HPA enabled | ✅ HPA compatible |
| **Health Probes** | ❌ Not configured | ❌ Not configured | ✅ Pre-configured | 🔧 Step 6 workflow |
| **Load Testing** | ✅ Basic endpoints | ✅ Basic endpoints | ✅ Built-in HPA triggers | ❌ Focus on probes |
| **CLI Focus** | Basic deployment | Basic deployment | ✅ Full CLI workflow | ✅ Probe configuration |
| **Production Ready** | Basic demo | Database ready | Resource optimized | Health monitoring |
| **Step Completion** | Static progress | Manual progression | Automatic scaling | Probe-based completion |

## Learning Path

The applications are designed to be used in sequence, with each building upon concepts from the previous version:

1. **Start with V1** → Understand ephemeral storage limitations and basic containerization
2. **Progress to V2** → Learn persistent storage patterns and database integration  
3. **Advance to V3** → Master resource management, scaling, and CLI operations
4. **Complete with V4** → Implement production health monitoring and probe configuration

## Key Kubernetes/OpenShift Concepts Demonstrated

### Container Fundamentals
- **Container lifecycle management** (V1-V4)
- **Resource requests and limits** (V3, V4)
- **Environment variable configuration** (V2-V4)
- **Multi-stage Docker builds** (All versions)

### Storage and Persistence  
- **Ephemeral storage limitations** (V1)
- **Persistent Volume Claims (PVC)** (V2-V4)
- **Database integration patterns** (V2-V4)
- **StatefulSet vs Deployment trade-offs** (V2-V4)

### Networking and Services
- **Service discovery and DNS** (All versions)
- **Route configuration with TLS termination** (All versions)  
- **Load balancing across pods** (V3, V4)
- **Health check integration** (V4)

### Scaling and Performance
- **Manual scaling operations** (V1, V2)
- **Horizontal Pod Autoscaler (HPA)** (V3)
- **Resource utilization monitoring** (V3, V4)
- **Load testing and traffic generation** (V3)

### Production Readiness
- **Health probe configuration** (V4)
- **Rolling deployments** (V3, V4)
- **Application lifecycle management** (V4)
- **Monitoring and troubleshooting** (All versions)

## Development Workflows

The repository includes automated task management via `mise.toml` for streamlined development across all applications:

### Local Development
```bash
# Install dependencies for all applications
mise run install-all

# V1 Development (Ephemeral Storage)
mise run v1-dev
mise run v1-docker-run     # Test with resource limits

# V2 Development (Persistent Storage)  
mise run v2-dev
mise run v2-docker-run     # Test with SQLite

# V3/V4 Development (Full OpenShift Features)
# Use V3 or V4 directories directly with standard Flask development

# Check-in App Development (Registration System)
mise run checkin-dev
```

### Container Testing
```bash
# Build and test containers locally
mise run v1-docker-run     # V1 with 256m RAM, 0.5 CPU limits
mise run v2-docker-run     # V2 with SQLite database

# Clean up containers
mise run clean-docker
```

## OpenShift Deployment

Each demo application includes comprehensive OpenShift deployment manifests:

### V1: Basic Containerization
```bash
cd demo-app-v1/
oc apply -f openshift/     # Basic deployment with resource limits
```

### V2: Persistent Storage
```bash
cd demo-app-v2/
oc apply -f openshift/postgresql.yaml    # Deploy database first
oc apply -f openshift/                   # Deploy app with persistence
```

### V3: Resource Management & CLI Focus
```bash
cd demo-app-v3/
# Follow comprehensive CLI workflow in demo-app-v3/README.md
oc apply -f openshift/postgresql.yaml
oc apply -f openshift/buildconfig.yaml
oc start-build demo-app-v3 --follow
oc apply -f openshift/deployment.yaml
oc apply -f openshift/service.yaml
oc apply -f openshift/route.yaml
oc apply -f openshift/hpa.yaml
```

### V4: Health Probe Configuration
```bash
cd demo-app-v4/
# Deploy without probes, then configure via CLI
# Follow health probe workflow in demo-app-v4/README.md
oc apply -f openshift/deployment.yaml   # No probes initially
# ... configure probes via oc patch commands
```

### Check-in App: Registration System
```bash
cd check-in-app/
./deploy.sh    # Automated deployment with PostgreSQL and secrets
```

## Common OpenShift Components

All applications include production-ready configurations:

- **BuildConfig**: Source-to-Image (S2I) builds from Git repositories
- **ImageStream**: Container image management and automatic deployment triggers  
- **Deployment**: Application pods with resource limits and environment configuration
- **Service**: Internal load balancing and service discovery
- **Route**: External HTTPS access with TLS edge termination
- **PostgreSQL**: Persistent database with PVC storage (V2-V4, Check-in)
- **Secrets**: Secure configuration management for database credentials
- **HPA**: Horizontal Pod Autoscaler for automatic scaling (V3)

## Repository Structure

```
tech-lab-demos/
├── demo-app-v1/          # Ephemeral storage demo
│   ├── app.py           # Flask application 
│   ├── openshift/       # Deployment manifests
│   └── README.md        # V1-specific documentation
├── demo-app-v2/          # Persistent storage demo  
│   ├── app.py           # Enhanced Flask with database
│   ├── openshift/       # Production manifests
│   └── README.md        # V2-specific documentation
├── demo-app-v3/          # Resource management & CLI demo
│   ├── app.py           # Resource monitoring features
│   ├── openshift/       # HPA and resource limits
│   └── README.md        # CLI-focused documentation
├── demo-app-v4/          # Health probe configuration demo
│   ├── app.py           # Probe detection logic
│   ├── openshift/       # Deployment without initial probes
│   └── README.md        # Health probe workflow guide
├── check-in-app/         # Lab registration system
│   ├── app.py           # Registration and admin features
│   ├── openshift/       # Production deployment
│   ├── deploy.sh        # Automated deployment script
│   └── README.md        # Registration system guide
├── mise.toml            # Development task automation
└── README.md            # This comprehensive overview
```

This comprehensive lab platform provides hands-on experience with container orchestration, storage management, resource optimization, health monitoring, and production deployment patterns in OpenShift environments.
