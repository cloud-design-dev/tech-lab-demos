# Step 4: Deploy Demo App V2 (Persistent Storage)

In this session, you'll deploy Demo App V2, which demonstrates persistent storage using PostgreSQL. You'll learn the difference between ephemeral and persistent data, and see how database integration solves real-world application requirements.

!!! info "Estimated Time"
    **Setup Time:** 25-30 minutes  
    **Learning Time:** 15-20 minutes

## 🎯 Learning Objectives

By the end of this step, you will:

- ✅ Deploy PostgreSQL database with persistent storage
- ✅ Deploy applications that connect to external databases
- ✅ Understand Persistent Volume Claims (PVCs) and storage classes
- ✅ Compare ephemeral vs persistent storage patterns
- ✅ Use `oc` commands for database and application management

## 📋 Prerequisites

Before starting this step:

- [ ] Completed [Step 3: Deploy Demo App V1](step-3-demo-app-v1.md)
- [ ] Have Demo App V1 running (for comparison)
- [ ] Access to `oc` CLI (or use IBM Cloud Shell)
- [ ] Understanding of database concepts

## 🏗️ Demo App V2 Overview

**Demo App V2** solves the persistence problems demonstrated in V1:

### Key Differences from V1
- 📊 **PostgreSQL Database** instead of in-memory storage
- 💾 **Persistent Volume Claims** for data survival
- 🔄 **Data survives** pod restarts, scaling, and updates
- 🎯 **Step 4 highlighted** in progress visualization
- ✅ **Production-ready** database integration patterns

### Architecture Comparison

=== "V1 - Ephemeral"
    ```mermaid
    graph TD
        A[User] --> B[Route]
        B --> C[Service] 
        C --> D[Pod]
        D --> E[Flask App]
        E --> F[In-Memory Dict]
        F -.->|Lost on Restart| X[💀]
        
        style F fill:#ffcdd2
    ```

=== "V2 - Persistent"
    ```mermaid
    graph TD
        A[User] --> B[Route]
        B --> C[Service]
        C --> D[Pod]
        D --> E[Flask App]
        E --> F[PostgreSQL]
        F --> G[PVC]
        G --> H[IBM Block Storage]
        
        style F fill:#c8e6c9
        style G fill:#e8f5e8
        style H fill:#e3f2fd
    ```

## 📁 Step 1: Clone the Repository and Set Up Environment

First, we'll clone the demo repository and examine the demo-app-v2 structure.

### 1. Clone the Repository

```bash
# Clone the tech-lab-demos repository
git clone https://github.com/cloud-design-dev/tech-lab-demos.git
cd tech-lab-demos

# Explore the demo-app-v2 directory structure
ls -la demo-app-v2/

# Check the OpenShift manifests
ls -la demo-app-v2/openshift/
```

### 2. Examine the V2 Architecture

```bash
# Review the application structure
cat demo-app-v2/README.md

# Look at the OpenShift deployment files
ls demo-app-v2/openshift/
# You should see:
# - postgresql.yaml (database deployment)
# - app-v2.yaml (application deployment)
```

## 🗄️ Step 2: Deploy PostgreSQL Database

We'll use the provided PostgreSQL manifest from the repository.

### 1. Deploy PostgreSQL with Persistent Storage

```bash
# Deploy PostgreSQL using the provided manifest
oc apply -f demo-app-v2/openshift/postgresql.yaml

# The manifest includes:
# - PersistentVolumeClaim (postgresql-pvc)
# - Secret (postgresql-secret) 
# - Service (postgresql-service)
# - Deployment (postgresql)
```

### 2. Verify PostgreSQL Deployment

```bash
# Check if PVC was created and bound
oc get pvc postgresql-pvc

# Expected output:
# NAME            STATUS   VOLUME                 CAPACITY   ACCESS MODES
# postgresql-pvc  Bound    pvc-abc123...         10Gi       RWO

# Check PostgreSQL pod status
oc get pods -l app=postgresql

# Wait for PostgreSQL to be ready
oc wait --for=condition=Ready pod -l app=postgresql --timeout=300s
```

### 3. Test Database Connectivity

```bash
# Connect to PostgreSQL and verify it's working
oc exec -it deployment/postgresql -- psql -U demo_user -d demo_db -c "SELECT version();"

# Should show PostgreSQL version information
```

## 🚀 Step 3: Deploy Demo App V2

Now we'll deploy the application using the provided manifest files.

### 1. Deploy Demo App V2 Using Command Line

```bash
# Deploy the application using the provided manifest
oc apply -f demo-app-v2/openshift/app-v2.yaml

# The manifest includes:
# - BuildConfig (builds from GitHub repo)
# - ImageStream (stores built images)
# - Deployment (runs the application)
# - Service (internal networking)
# - Route (external access with HTTPS)
```

### 2. Alternative: Step-by-Step Deployment

If you prefer to understand each component, you can deploy them individually:

```bash
# Create the BuildConfig and ImageStream
oc apply -f - <<EOF
apiVersion: build.openshift.io/v1
kind: BuildConfig
metadata:
  name: demoapp2
spec:
  source:
    type: Git
    git:
      uri: https://github.com/cloud-design-dev/tech-lab-demos.git
    contextDir: demo-app-v2
  strategy:
    type: Source
    sourceStrategy:
      from:
        kind: ImageStreamTag
        namespace: openshift
        name: python:3.11
  output:
    to:
      kind: ImageStreamTag
      name: demoapp2:latest
---
apiVersion: image.openshift.io/v1
kind: ImageStream
metadata:
  name: demoapp2
EOF

# Start the build
oc start-build demoapp2 --follow
```

### 3. Monitor the Deployment Process

```bash
# Monitor the build process
oc get builds -w

# Watch build logs (in a separate terminal)
oc logs -f bc/demoapp2

# Check build completion
oc get builds -l buildconfig=demoapp2

# Monitor deployment rollout
oc rollout status deployment/demoapp2 --timeout=300s
```

### 4. Verify Application Deployment

```bash
# Check all components are running
oc get pods -l app=demoapp2

# Verify the route was created
oc get route demoapp2

# Test application connectivity
APP_URL=$(oc get route demoapp2 -o jsonpath='{.spec.host}')
echo "Demo App V2 URL: https://$APP_URL"

# Test the health endpoint
curl -k https://$APP_URL/api/health
```

## 📊 Step 4: Compare V1 vs V2 Behavior

Now you can directly compare the persistence behavior between the two applications.

### 1. Access Both Applications

```bash
# Get both application URLs
echo "V1 (Ephemeral): https://$(oc get route demoapp1 -o jsonpath='{.spec.host}')"
echo "V2 (Persistent): https://$(oc get route demoapp2 -o jsonpath='{.spec.host}')"
```

### 2. Test Persistence in Both Apps

**In Demo App V1:**
1. Click **"Test Persistence"** to add data
2. Note the entries appear
3. Click **"Reload Page (Demo Reset)"**  
4. ❌ Data disappears (ephemeral storage)

**In Demo App V2:**
1. Click **"Test Persistence"** to add data
2. Note the entries appear  
3. Click **"Reload Page"** (no reset - data persists!)
4. ✅ Data remains (persistent storage)

### 3. Test Pod Restart Persistence

```bash
# Restart the V2 application pod
oc delete pod -l app=demoapp2

# Wait for new pod to start
oc wait --for=condition=Ready pod -l app=demoapp2

# Check the V2 app - data should still be there!
# Check the V1 app - data will be gone (if any was added since last restart)
```

## 🔍 Step 5: Explore Storage Concepts

### 1. Examine Persistent Volume Claims

```bash
# List all PVCs in your project
oc get pvc

# Get detailed information about the PostgreSQL PVC
oc describe pvc postgresql-pvc

# Check storage class details
oc get storageclass ibmc-vpc-block-5iops-tier -o yaml
```

### 2. View Database Data

```bash
# Connect to PostgreSQL and examine the data
oc exec -it deployment/postgresql -- psql -U demo_user -d demo_db

# In the PostgreSQL shell, run:
# \dt                    -- List tables
# SELECT * FROM entries;  -- View stored data
# \q                     -- Quit
```

### 3. Monitor Resource Usage

```bash
# Check storage usage
oc exec -it deployment/postgresql -- df -h /var/lib/postgresql/data

# View pod resource consumption
oc adm top pods -l app=postgresql
oc adm top pods -l app=demoapp2
```

## 📈 Step 6: Database Operations

### 1. Scale the Application (Database Persists)

```bash
# Scale Demo App V2 to 3 replicas
oc scale deployment demoapp2 --replicas=3

# Watch the scaling
oc get pods -l app=demoapp2 -w

# Test the application - all pods connect to the same database
# Data is shared across all application instances!
```

### 2. Backup Considerations (Demo Only)

```bash
# Example: Create a database dump (educational purposes)
oc exec -it deployment/postgresql -- pg_dump -U demo_user demo_db > /tmp/backup.sql

# In production, you'd use proper backup tools and PVC snapshots
```

## 🎓 Key Concepts Demonstrated

### Storage Patterns
- **Ephemeral Storage (V1):** Fast but temporary, lost on restart
- **Persistent Storage (V2):** Survives pod lifecycle, enables stateful apps
- **Shared Storage:** Multiple app instances can share the same database

### OpenShift Storage
- **PersistentVolumeClaim (PVC):** Request for storage resources
- **Storage Classes:** Define types of available storage (performance, features)
- **Volume Mounts:** How containers access persistent storage

### Database Integration
- **Environment Variables:** Secure way to pass connection details
- **Kubernetes Secrets:** Store sensitive data like passwords
- **Service Discovery:** Applications find databases via service names

## ✅ Verification Checklist

You've successfully completed Step 4 when:

- ✅ PostgreSQL is running with persistent storage (PVC bound)
- ✅ Demo App V2 is deployed and connects to the database
- ✅ Data persists through page reloads in V2 (unlike V1)
- ✅ Data survives pod restarts in V2
- ✅ Application shows "Step 4" as highlighted/current
- ✅ You can scale V2 and all instances share the same data

## 🔍 Troubleshooting

### Common Issues

**PostgreSQL pod won't start**
```bash
# Check events and logs
oc describe pod -l app=postgresql
oc logs deployment/postgresql
```

**App can't connect to database**
```bash
# Verify service connectivity
oc exec -it deployment/demoapp2 -- nslookup postgresql-service

# Check environment variables
oc set env deployment/demoapp2 --list
```

**PVC stuck in Pending**
```bash
# Check storage class availability
oc get storageclass
oc describe pvc postgresql-pvc
```

## 📝 What's Next?

The persistent storage you've implemented in Demo App V2 solves the data loss problem from V1, but now we need to address performance and scalability. 

In **Step 5**, you'll deploy Demo App V3 which focuses on:
- 📈 **Resource Management** with CPU and memory limits
- ⚡ **Horizontal Pod Autoscaling** based on load
- 🔧 **Advanced `oc` commands** for scaling and monitoring
- 📊 **Load testing** to trigger scaling events

---

**Ready for scaling and resource management?** 🚀 [Continue to Step 5: Resource Management →](step-5-demo-app-v3.md)

*Congratulations! You've successfully implemented persistent storage and understand the fundamental difference between ephemeral and persistent data in containerized applications.* 🎉