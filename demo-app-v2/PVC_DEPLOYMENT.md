# V2 Demo App with Persistent Volume Claims (PVC)

This guide demonstrates how to deploy the V2 demo app with persistent SQLite storage using OpenShift PVCs, perfect for showcasing persistent storage concepts.

## Overview

The V2 app now supports three storage modes:
1. **PostgreSQL** (production) - Full database server with networked storage
2. **SQLite with PVC** (demonstration) - File-based database with persistent storage  
3. **SQLite in /tmp** (local development) - Ephemeral storage

## PVC Deployment Steps

### Step 1: Import from Git (Creates Basic App Components)
```bash
# Use OpenShift Console: Developer View > Add > Import from Git
# URL: https://github.com/your-repo/tech-labs-dallas
# Context Dir: /demo-app-v2
# This creates: BuildConfig, DeploymentConfig, Service, Route
```

**Important**: "Import from Git" does NOT automatically apply YAML files from the `openshift/` directory.

### Step 2: Apply PVC and Storage Configuration
```bash
# Apply the PVC for SQLite storage
oc apply -f demo-app-v2/openshift/sqlite-pvc.yaml

# Update the DeploymentConfig to use PVC
oc apply -f demo-app-v2/openshift/app-v2.yaml
```

### Step 3: Verify PVC is Mounted
```bash
# Check PVC status
oc get pvc v2-sqlite-pvc

# Verify volume mount in pod
oc describe pod -l app=openshift-demo-app-v2

# Check SQLite database location
oc exec deployment/openshift-demo-app-v2 -- ls -la /app/data/
```

## Storage Configuration Details

### PVC Specifications
- **Name**: `v2-sqlite-pvc`
- **Size**: 1Gi
- **Access Mode**: ReadWriteOnce
- **Mount Path**: `/app/data`
- **SQLite File**: `/app/data/v2_demo.db`

### Environment Variables
```yaml
- name: SQLITE_PATH
  value: "/app/data/v2_demo.db"  # Points to PVC-mounted storage
```

### Volume Configuration
```yaml
volumeMounts:
- name: sqlite-storage
  mountPath: /app/data

volumes:
- name: sqlite-storage
  persistentVolumeClaim:
    claimName: v2-sqlite-pvc
```

## Demonstration Scenarios

### Scenario 1: Data Persistence Across Pod Restarts
```bash
# 1. Add test data via the web UI or API
curl -X POST https://your-app-route/api/persistence/test \\
  -H "Content-Type: application/json" \\
  -d '{"data": "PVC test data"}'

# 2. Delete the pod (triggers restart)
oc delete pod -l app=openshift-demo-app-v2

# 3. Verify data persists after restart
curl https://your-app-route/api/persistence/stats
```

### Scenario 2: Scaling Demonstration
```bash
# 1. Add test data
# 2. Scale to multiple replicas
oc scale dc/openshift-demo-app-v2 --replicas=3

# 3. Verify all pods share the same PVC data
oc exec deployment/openshift-demo-app-v2 -- cat /app/data/v2_demo.db
```

### Scenario 3: Storage Type Comparison
- **V1 App**: Ephemeral storage (data lost on restart)
- **V2 App with PVC**: Persistent storage (data survives restarts)
- **V2 App with PostgreSQL**: Full database persistence

## API Endpoints for Testing

### Test Persistence
```bash
# Add test entry
POST /api/persistence/test
{"data": "Your test data"}

# Check all entries  
GET /api/persistence/stats

# View database info
GET /api/debug/db
```

### Expected Response (with PVC)
```json
{
  "total_entries": 3,
  "database_type": "SQLite", 
  "database_url": "sqlite:////app/data/v2_demo.db",
  "latest_entry": {
    "id": 3,
    "data": "PVC test data",
    "timestamp": "2025-08-13T23:45:12.123456"
  }
}
```

## Troubleshooting

### PVC Not Mounting
```bash
# Check PVC status
oc get pvc v2-sqlite-pvc

# Check pod events
oc describe pod -l app=openshift-demo-app-v2 | grep -A 10 Events

# Verify storage class exists
oc get storageclass
```

### SQLite Permission Issues
```bash
# Check directory permissions
oc exec deployment/openshift-demo-app-v2 -- ls -la /app/

# Verify app can write to PVC
oc exec deployment/openshift-demo-app-v2 -- touch /app/data/test-file
```

### Fallback Behavior
If PVC mounting fails, the app automatically falls back to `/tmp/v2_demo.db` (ephemeral storage).

## Educational Value

This PVC setup demonstrates:
1. **Persistent vs Ephemeral Storage** - Data survives pod restarts
2. **Volume Mounting** - How containers access external storage
3. **Storage Classes** - Different types of persistent storage
4. **Scaling with Shared Storage** - Multiple pods accessing same data
5. **Storage Management** - PVC lifecycle and administration

Perfect for OpenShift storage demonstrations and container orchestration education!