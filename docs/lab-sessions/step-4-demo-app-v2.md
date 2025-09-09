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

## 🗄️ Step 1: Deploy PostgreSQL Database

First, we'll deploy PostgreSQL with persistent storage using `oc` commands.

### 1. Create PostgreSQL Resources

```bash
# Create the PostgreSQL deployment with persistent storage
oc apply -f - <<EOF
---
# PostgreSQL Persistent Volume Claim
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgresql-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: ibmc-vpc-block-5iops-tier
---
# PostgreSQL Secret
apiVersion: v1
kind: Secret
metadata:
  name: postgresql-secret
type: Opaque
data:
  # Base64 encoded values
  # username: demo_user
  # password: SecurePass123!
  # database: demo_db
  POSTGRES_USER: ZGVtb191c2Vy
  POSTGRES_PASSWORD: U2VjdXJlUGFzczEyMyE=
  POSTGRES_DB: ZGVtb19kYg==
---
# PostgreSQL Service
apiVersion: v1
kind: Service
metadata:
  name: postgresql-service
spec:
  selector:
    app: postgresql
  ports:
    - port: 5432
      targetPort: 5432
  type: ClusterIP
---
# PostgreSQL Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgresql
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgresql
  template:
    metadata:
      labels:
        app: postgresql
    spec:
      containers:
      - name: postgresql
        image: postgres:15-alpine
        env:
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgresql-secret
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgresql-secret
              key: POSTGRES_PASSWORD
        - name: POSTGRES_DB
          valueFrom:
            secretKeyRef:
              name: postgresql-secret
              key: POSTGRES_DB
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgresql-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "250m"
      volumes:
      - name: postgresql-storage
        persistentVolumeClaim:
          claimName: postgresql-pvc
EOF
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

## 🚀 Step 2: Deploy Demo App V2

Now we'll deploy the application that connects to PostgreSQL.

### 1. Deploy Demo App V2 Using Import from Git

You have two options for deployment:

=== "Option A: Web Console (Recommended)"

    1. Go to **Developer** view → **+Add** → **Import from Git**
    2. **Git Repository:**
       ```
       https://github.com/cloud-design-dev/tech-lab-demos
       ```
    3. **Advanced Git Options:**
       - **Context dir:** `demo-app-v2`
    4. **General Settings:**
       - **Application:** `[group-letter]-demo-apps` (same as V1)
       - **Name:** `demoapp2`
    5. **Advanced Options:**
       - **Target Port:** `8080`
       - **Create Route:** ✅ Enabled
       - **Secure Route:** ✅ Enabled
       - **TLS Termination:** Edge
    6. **Environment Variables:** (Add these in Advanced Options)
       - `POSTGRES_HOST` = `postgresql-service`
       - `POSTGRES_PORT` = `5432` 
       - `POSTGRES_USER` = `demo_user`
       - `POSTGRES_PASSWORD` = `SecurePass123!`
       - `POSTGRES_DB` = `demo_db`

=== "Option B: Command Line"

    ```bash
    # Create Demo App V2 using oc new-app
    oc new-app https://github.com/cloud-design-dev/tech-lab-demos \
      --context-dir=demo-app-v2 \
      --name=demoapp2 \
      --env POSTGRES_HOST=postgresql-service \
      --env POSTGRES_PORT=5432 \
      --env POSTGRES_USER=demo_user \
      --env POSTGRES_PASSWORD=SecurePass123! \
      --env POSTGRES_DB=demo_db
    
    # Create a route for external access
    oc expose service demoapp2 \
      --port=8080 \
      --hostname=demoapp2-${GROUP_LETTER}-project.apps.your-cluster.domain.com
    
    # Enable HTTPS
    oc patch route demoapp2 -p '{"spec":{"tls":{"termination":"edge","insecureEdgeTerminationPolicy":"Redirect"}}}'
    ```

### 2. Monitor the Build Process

```bash
# Watch the build logs
oc logs -f bc/demoapp2

# Check build status
oc get builds

# Wait for deployment to complete
oc rollout status deployment/demoapp2 --timeout=300s
```

### 3. Verify Application Deployment

```bash
# Check that all pods are running
oc get pods -l app=demoapp2

# Get the application route
oc get route demoapp2 -o jsonpath='{.spec.host}'

# Test the application endpoint
curl -k https://$(oc get route demoapp2 -o jsonpath='{.spec.host}')/api/health
```

## 📊 Step 3: Compare V1 vs V2 Behavior

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

## 🔍 Step 4: Explore Storage Concepts

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

## 📈 Step 5: Database Operations

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