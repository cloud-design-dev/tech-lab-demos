# OpenShift Deployment for Check-in App

This directory contains OpenShift manifests for deploying the check-in application with PostgreSQL backend.

## Architecture

- **PostgreSQL Database**: 20GB persistent storage using `ibmc-vpc-block-5iops-tier`
- **Check-in App**: Python Flask application with IBM Cloud SDK integration
- **High Availability**: 2 replicas with rolling updates
- **Security**: Secrets for sensitive data, HTTPS with edge TLS termination

## Prerequisites

1. OpenShift CLI (`oc`) installed and configured
2. Logged in to OpenShift cluster: `oc login`
3. IBM Cloud API Key and Account ID (for user validation)

## Deployment

### Quick Deployment

```bash
# Set IBM Cloud credentials (required for production)
export IBM_CLOUD_API_KEY="your-api-key-here"
export IBM_CLOUD_ACCOUNT_ID="your-account-id-here"

# Run deployment script
./deploy.sh
```

### Manual Deployment

1. **Deploy PostgreSQL:**
   ```bash
   oc apply -f postgresql.yaml
   oc wait --for=condition=available --timeout=300s deployment/postgresql
   ```

2. **Update IBM Cloud credentials in secret:**
   ```bash
   # Edit checkin-app.yaml and update the secret with base64 encoded values:
   echo -n "your-api-key" | base64
   echo -n "your-account-id" | base64
   ```

3. **Deploy Check-in App:**
   ```bash
   oc apply -f checkin-app.yaml
   oc start-build checkin-app --wait
   oc rollout status dc/checkin-app
   ```

## Configuration

### Database Configuration

The PostgreSQL deployment includes:
- **Storage**: 20GB PVC with IBM Cloud VPC Block Storage (5 IOPS/GB)
- **Credentials**: Stored in `postgresql-secret`
  - Username: `checkin_user`
  - Password: `SecurePass123!` (change in production)
  - Database: `checkin_db`

### Application Configuration

Environment variables are managed through:
- **Secrets**: `checkin-app-secret` (sensitive data)
  - IBM Cloud API Key/Account ID
  - Flask secret key
  - Admin password
- **ConfigMap**: `checkin-app-config` (non-sensitive)
  - Database connection details
  - Environment settings

### Default Credentials

- **Admin Password**: `demo-admin-2024`
- **Database Password**: `SecurePass123!`

**⚠️ Change these in production!**

## Security Best Practices

1. **Update Secrets**: Replace default passwords with secure values
2. **IBM Cloud Integration**: Set proper API key and account ID
3. **Network Policies**: Consider implementing network policies for additional security
4. **Resource Limits**: Adjust CPU/memory limits based on usage patterns

## Storage Configuration

The PostgreSQL PVC uses IBM Cloud VPC Block Storage:
- **Storage Class**: `ibmc-vpc-block-5iops-tier`
- **Size**: 20GB
- **Performance**: 5 IOPS per GB (100 IOPS total)
- **Access Mode**: ReadWriteOnce

## Scaling

### Application Scaling
```bash
oc scale dc/checkin-app --replicas=3
```

### Database Scaling
PostgreSQL runs as a single replica (stateful). For high availability:
- Consider PostgreSQL clustering solutions
- Implement database backups
- Use read replicas for read-heavy workloads

## Monitoring

Health check endpoints:
- **Application**: `GET /api/health`
- **Database Status**: `GET /api/stats`

Monitoring URLs (replace with your route):
```bash
APP_URL=$(oc get route checkin-app-route -o jsonpath='{.spec.host}')
curl https://$APP_URL/api/health
curl https://$APP_URL/api/stats
```

## Troubleshooting

### Check Pod Status
```bash
oc get pods -l app=postgresql
oc get pods -l app=checkin-app
```

### View Logs
```bash
oc logs deployment/postgresql
oc logs dc/checkin-app
```

### Database Connection Issues
```bash
# Check database connectivity from app pod
oc rsh deployment/checkin-app
# Inside pod:
python -c "
import os, psycopg2
conn = psycopg2.connect(
    host=os.environ['POSTGRES_HOST'],
    user=os.environ['POSTGRES_USER'], 
    password=os.environ['POSTGRES_PASSWORD'],
    database=os.environ['POSTGRES_DB']
)
print('Database connection successful!')
"
```

### Storage Issues
```bash
oc get pvc postgresql-pvc
oc describe pvc postgresql-pvc
```

## Backup and Recovery

### Database Backup
```bash
# Create backup job
oc create job --from=cronjob/postgres-backup backup-$(date +%Y%m%d)
```

### Application Data Export
```bash
# Export user data via API
curl -u admin:demo-admin-2024 https://$APP_URL/api/registered > backup.json
```

## Clean Up

Remove all resources:
```bash
oc delete -f checkin-app.yaml
oc delete -f postgresql.yaml
```

**⚠️ Warning**: This will delete all data including the PostgreSQL database!