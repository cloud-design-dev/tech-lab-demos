# IBM Cloud Code Engine Deployment

This directory contains configuration and deployment scripts for running the check-in app on IBM Cloud Code Engine with IBM Cloud Databases for PostgreSQL.

## Prerequisites

1. IBM Cloud CLI with Code Engine plugin
2. IBM Cloud Databases for PostgreSQL instance
3. IBM Cloud API key with appropriate permissions

## Environment Setup

The application expects the following environment variables in Code Engine:

### Required Variables
- `DATABASES_FOR_POSTGRESQL_CONNECTION` - JSON connection string from IBM Cloud Databases
- `IBM_CLOUD_API_KEY` - API key for user validation
- `IBM_CLOUD_ACCOUNT_ID` - Account ID for user validation
- `FLASK_SECRET_KEY` - Secret key for Flask sessions
- `ADMIN_PASSWORD` - Admin dashboard password

### Optional Variables
- `PORT` - Application port (default: 8080)

## Deployment Steps

1. **Create PostgreSQL Database**
   ```bash
   ibmcloud resource service-instance-create checkin-postgres databases-for-postgresql standard us-south
   ```

2. **Get Database Connection Info**
   ```bash
   ibmcloud resource service-key-create checkin-postgres-key Manager --instance-name checkin-postgres
   ibmcloud resource service-key checkin-postgres-key
   ```

3. **Deploy to Code Engine**
   ```bash
   # Create Code Engine project
   ibmcloud ce project create --name checkin-app
   
   # Build and deploy application
   ibmcloud ce application create --name checkin-app \
     --image icr.io/namespace/checkin-app:latest \
     --port 8080 \
     --env DATABASES_FOR_POSTGRESQL_CONNECTION='{"connection":{"postgres":{"..."}}}' \
     --env IBM_CLOUD_API_KEY=your-api-key \
     --env IBM_CLOUD_ACCOUNT_ID=your-account-id \
     --env FLASK_SECRET_KEY=your-secret-key \
     --env ADMIN_PASSWORD=your-admin-password
   ```

## Database Connection Format

The `DATABASES_FOR_POSTGRESQL_CONNECTION` environment variable should contain the full JSON connection object from IBM Cloud Databases, including SSL certificates.

Example structure:
```json
{
  "connection": {
    "postgres": {
      "authentication": {
        "method": "direct",
        "password": "password", # pragma: allowlist secret
        "username": "username"
      },
      "certificate": {
        "certificate_base64": "LS0tLS1CRUdJTi...",
        "name": "certificate-name"
      },
      "database": "ibmclouddb",
      "host": "host.databases.appdomain.cloud",
      "port": 5432
    }
  }
}
```

## Health Check

The application provides a health endpoint at `/api/health` that Code Engine can use for readiness and liveness probes.

## Scaling

Code Engine will automatically scale the application based on traffic. The application is stateless and can handle multiple instances.
