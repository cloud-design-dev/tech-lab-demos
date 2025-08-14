# V2 Deployment Guide with PostgreSQL

## Prerequisites
1. OpenShift cluster access with `oc` CLI
2. Project created: `oc new-project rst-demo-lab`
3. GitHub repository with the code

## Step-by-Step Deployment

### 1. Update BuildConfig with your GitHub repository
Edit `v2/openshift/buildconfig.yaml` and replace:
```
uri: https://github.com/your-username/tech-labs-dallas.git
```
With your actual GitHub repository URL.

### 2. Deploy PostgreSQL Database First
```bash
# Apply database resources
oc apply -f v2/openshift/postgresql.yaml

# Wait for PostgreSQL to be ready (this may take a few minutes)
oc wait --for=condition=Ready pod -l app=postgresql --timeout=300s
```

### 3. Deploy Application BuildConfig and ImageStream
```bash
# Create the build configuration
oc apply -f v2/openshift/buildconfig.yaml

# Start the build from your GitHub repository
oc start-build openshift-demo-app-v2 --follow
```

### 4. Deploy Application
```bash
# Deploy the application with database connection
oc apply -f v2/openshift/app-v2.yaml

# Check the deployment status
oc get pods -l app=openshift-demo-app-v2
```

### 5. Get the Application URL
```bash
oc get route openshift-demo-app-v2
```

## Troubleshooting

### If S2I build fails:
1. Check if the GitHub repository URL is correct
2. Verify the `v2` directory contains all required files
3. Check build logs: `oc logs -f build/openshift-demo-app-v2-1`

### If database connection fails:
1. Verify PostgreSQL pod is running: `oc get pods -l app=postgresql`
2. Check database logs: `oc logs -f deployment/postgresql`
3. Verify secret exists: `oc get secret postgresql-secret`

### Environment Variables
The app expects the following environment variable (automatically set by app-v2.yaml):
- `DATABASE_URL`: PostgreSQL connection string (from secret)

When properly deployed, the app will:
1. Use PostgreSQL for persistence (not SQLite)
2. Display container resource metrics
3. Show pod hostname for scaling demos
4. Maintain data persistence across pod restarts