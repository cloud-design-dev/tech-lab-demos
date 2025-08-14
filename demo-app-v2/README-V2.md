# OpenShift Demo App - V2 with Database Persistence

This is Version 2 of the OpenShift Demo Lab application, featuring **real database persistence** to demonstrate persistent storage in OpenShift.

## What's New in V2

### 🗄️ Database Persistence
- **PostgreSQL integration** with SQLAlchemy ORM
- **Real data persistence** that survives pod restarts
- **Database connection fallback** to SQLite for local development
- **Enhanced Test Persistence button** showing actual DB entries

### 📊 Enhanced Features
- **Database statistics** endpoint showing total entries and connection info
- **Improved error handling** with database rollback capabilities
- **Step 4 focus** - "Add Persistence" is now the current step
- **Version 2.0.0** branding throughout the app

## Deployment Options

### Local Development (SQLite)
```bash
cd v2/
python -m pip install -r requirements.txt
python app.py
# Uses SQLite database: demo.db
```

### OpenShift with PostgreSQL
```bash
# Deploy PostgreSQL first
oc apply -f openshift/postgresql.yaml

# Deploy V2 app with database connection  
oc new-app registry.redhat.io/ubi8/python-39~. --name=openshift-demo-app-v2
oc apply -f openshift/app-v2.yaml
```

## Database Schema

### PersistenceTest Table
- `id` (Integer, Primary Key) - Auto-incrementing entry ID
- `data` (String, 500 chars) - Test data content  
- `timestamp` (DateTime) - Creation timestamp (UTC)

## API Endpoints

### New V2 Endpoints
- `GET /api/persistence/stats` - Database statistics and connection info
- `POST /api/persistence/test` - Create new database entry (enhanced)
- `GET /api/persistence/data` - List all database entries (enhanced)

### Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Application port (default: 8080)

## Demo Flow Comparison

### V1 (In-Memory)
1. Click "Test Persistence" → Creates memory entry
2. Click "Reload Page" → All data lost (ID resets to 1)

### V2 (Database)  
1. Click "Test Persistence" → Creates database entry
2. Click "Reload Page" → Data persists! (ID continues incrementing)
3. Shows total database entries and connection type

## OpenShift Resources

### PostgreSQL Deployment
- **Secret**: Database credentials (demo/demo_password)
- **PVC**: 1GB persistent volume for database storage
- **Deployment**: PostgreSQL 15 container with resource limits
- **Service**: Internal database service on port 5432

### V2 App Deployment  
- **Deployment**: App container with DATABASE_URL environment variable
- **Service**: HTTP service on port 8080
- **Route**: Secure HTTPS route with edge TLS termination

This demonstrates the power of persistent storage in OpenShift - data survives application restarts, scaling events, and pod migrations!# Updated Tue Aug 12 15:05:46 CDT 2025
