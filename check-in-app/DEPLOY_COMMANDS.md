# Check-in App OpenShift Deployment Commands

## Quick Deployment Reference

### Prerequisites
```bash
# Ensure you're logged into OpenShift
oc login --server=https://your-openshift-cluster-url

# Create or switch to your project/namespace
oc new-project tech-lab-demo
# OR
oc project tech-lab-demo
```

### Method 1: Automated Deployment (Recommended)
```bash
cd check-in-app/openshift/
./deploy.sh
```

### Method 2: Manual Step-by-Step Deployment

#### 1. Deploy PostgreSQL Database
```bash
cd check-in-app/openshift/
oc apply -f postgresql.yaml

# Wait for PostgreSQL to be ready
oc wait --for=condition=available --timeout=300s deployment/postgresql
```

#### 2. Deploy Check-in Application
```bash
# Apply all check-in app resources
oc apply -f checkin-app.yaml

# Start the S2I build
oc start-build checkin-app --wait

# Wait for deployment to complete
oc rollout status deployment/checkin-app --timeout=300s
```

#### 3. Get Application URL
```bash
# Get the route URL
oc get route checkin-app-route -o jsonpath='{.spec.host}'

# Or view all routes
oc get routes
```

## Configuration Commands

### Update IBM Cloud Credentials (Production)
```bash
# Set your credentials as environment variables
export IBM_CLOUD_API_KEY="your-api-key-here" # pragma: allowlist secret
export IBM_CLOUD_ACCOUNT_ID="your-account-id-here"

# Update the secret with base64 encoded values
oc patch secret checkin-app-secret --patch "{
  \"data\": {
    \"IBM_CLOUD_API_KEY\": \"$(echo -n $IBM_CLOUD_API_KEY | base64 | tr -d '\n')\",
    \"IBM_CLOUD_ACCOUNT_ID\": \"$(echo -n $IBM_CLOUD_ACCOUNT_ID | base64 | tr -d '\n')\"
  }
}"

# Restart deployment to pick up new credentials
oc rollout restart deployment/checkin-app
```

### Update Admin Password
```bash
# Set new admin password
NEW_ADMIN_PASSWORD="your-secure-password-here" # pragma: allowlist secret

oc patch secret checkin-app-secret --patch "{
  \"data\": {
    \"ADMIN_PASSWORD\": \"$(echo -n $NEW_ADMIN_PASSWORD | base64 | tr -d '\n')\"
  }
}"

# Restart deployment
oc rollout restart deployment/checkin-app
```

## Monitoring Commands

### Check Application Status
```bash
# View all pods
oc get pods -l app=checkin-app
oc get pods -l app=postgresql

# View deployments
oc get deployment checkin-app postgresql

# View services
oc get svc -l app=checkin-app
oc get svc -l app=postgresql

# View routes
oc get routes checkin-app-route
```

### Check Logs
```bash
# Application logs
oc logs deployment/checkin-app -f

# Database logs
oc logs deployment/postgresql -f

# Build logs
oc logs bc/checkin-app -f
```

### Check Storage
```bash
# View persistent volume claims
oc get pvc postgresql-pvc

# Check storage usage
oc describe pvc postgresql-pvc
```

## Scaling Commands

### Scale Application
```bash
# Scale to 3 replicas
oc scale deployment checkin-app --replicas=3

# Check scaling status
oc get deployment checkin-app
```

## Troubleshooting Commands

### Debug Pods
```bash
# Describe problematic pods
oc describe pod <pod-name>

# Get events
oc get events --sort-by=.metadata.creationTimestamp

# Check secrets
oc get secrets checkin-app-secret -o yaml
oc get secrets postgresql-secret -o yaml
```

### Database Connection Test
```bash
# Connect to PostgreSQL pod for debugging
oc exec -it deployment/postgresql -- psql -U checkin_user -d checkin_db

# Test database connectivity from app pod
oc exec -it deployment/checkin-app -- python -c "
import psycopg2
import os
conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    database=os.getenv('POSTGRES_DB')
)
print('Database connection successful!')
conn.close()
"
```

## Cleanup Commands

### Remove Application (Keep Data)
```bash
# Remove app deployment and services (keeps database and PVC)
oc delete -f checkin-app.yaml
```

### Complete Removal (INCLUDING DATA)
```bash
# Remove everything including database and persistent storage
oc delete -f checkin-app.yaml
oc delete -f postgresql.yaml

# Note: This will permanently delete all registration data!
```

## GitHub Webhook Setup

### Get Webhook URL
```bash
# Get the webhook URL for GitHub integration
oc describe bc/checkin-app | grep "Webhook GitHub:"
```

### Configure in GitHub
1. Go to your repository Settings → Webhooks
2. Add webhook with:
   - **Payload URL**: The webhook URL from above
   - **Content Type**: application/json
   - **Secret**: `webhook-secret-2024` (change in production)
   - **Events**: Just push events

## Resource Information

### Default Configuration
- **Application**: 2 replicas, 256Mi-512Mi memory, 100m-500m CPU
- **PostgreSQL**: 1 replica, 256Mi-512Mi memory, 250m-500m CPU, 20GB storage
- **Storage Class**: `ibmc-vpc-block-5iops-tier` (IBM Cloud VPC Block Storage)

### Network Access
- **Application Route**: HTTPS with edge TLS termination
- **Health Check**: `/api/health`
- **Registration API**: `/api/checkin`, `/api/lookup`

## Group Management Features

The check-in app now supports:
- **Group Letters**: A-Y (25 groups total)
- **VPC Mapping**: 5 groups per VPC (A-E → VPC 1, F-J → VPC 2, etc.)
- **User Interface**: Shows group letter and VPC assignment
- **Admin Dashboard**: Displays group letters and VPC assignments
- **API Responses**: Include group letter and VPC information
