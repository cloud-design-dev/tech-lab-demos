# Demo App Version 2

Follow this guide to deploy our demo app to OpenShift with persistent storage. 

## Prerequisites

Before deploying, you'll need to generate unique database credentials to avoid conflicts with other users.

### Generate Unique Database Password

**Important**: Use a unique password to prevent conflicts with other deployments. Run these commands to generate secure credentials:

```bash
# Generate a random 16-character password
DB_PASSWORD=$(openssl rand -base64 12 | tr -d "=+/")
echo "Generated password: $DB_PASSWORD"

# Or use a simpler approach with your username
DB_PASSWORD="$(whoami)_$(date +%s)"
echo "Generated password: $DB_PASSWORD"
```

**Save your password** - you'll need it for both deployment and verification steps.

## Steps

### Deploying the second demo app

You should end up on the `default` project dashboard. If not, select `default` from the project dropdown in the upper left hand corner of the page. Click on `Add` in the left hand navigation to start the app deployment process.

![Add new app](../images/roks-add-app.png)

- Click the `Import from Git` option
    - Git Repo URL: https://github.com/cloud-design-dev/tech-lab-demos.git
	    - Expand `Show Advanced Git options`
		    - Git reference: No changes needed
			- Context dir: `/demo-app-v2`
			- Source Secret: No changes needed
	- Dockerfile build and deploy configuration
	    - General:
		    - Application name: `<group-name>-demo-apps`
			- Name: `demoapp2`
		- Build: No changes needed
		- Deploy: No changes needed
		- Advanced Options:
			- Target Port: Select `8080` from the dropdown
			- Expand Show advanced Routing options
			    - Ensure that Secure Route is selected, TLS Termination is set to Edge, and Insecure Traffic is set to Redirect
				- All other settings can be left as is 
		- Click Create to start the build and deploy of the demo app
	- You should be taken to the Topology view of the `default` project where you can see the build and deployment process
		- Under Build section, click `View Logs` to look at Build Logs
        - Once the build is complete, you should see a green check mark next to the build icon
		- Click back to Topology view
		    - Show Running pods
			- Click Route link to visit the demo app  
			- Test persistence (it should know retain the count even after refreshing the page)

## App Verification

After deploying the app, verify database connectivity:

```bash
# Get the app route URL
APP_URL=$(oc get route openshift-demo-app-v2 -o jsonpath='{.spec.host}')
echo "App URL: https://$APP_URL"

# Test persistence API endpoint
curl -k "https://$APP_URL/api/persistence/stats"

# Should show PostgreSQL connection:
# {"database_type": "PostgreSQL", "total_entries": 0, ...}
```

If the app shows SQLite instead of PostgreSQL:
```bash
# Check app logs for database connection errors
oc logs deployment/openshift-demo-app-v2

# Verify DATABASE_URL environment variable is set
oc set env deployment/openshift-demo-app-v2 --list | grep DATABASE
```

## Demo Flow Comparison

### V1 (In-Memory)
1. Click "Test Persistence" → Creates memory entry
2. Click "Reload Page" → All data lost (ID resets to 1)

### V2 (Database)  
1. Click "Test Persistence" → Creates database entry
2. Click "Reload Page" → Data persists! (ID continues incrementing)
3. Shows total database entries and connection type

## Database Deployment

### Deploy PostgreSQL with Custom Credentials

Before deploying the app, you need to deploy PostgreSQL with your unique password:

```bash
# Replace YOUR_PASSWORD with the password you generated above
export DB_PASSWORD="YOUR_UNIQUE_PASSWORD_HERE" # pragma: allowlist secret

# Create the PostgreSQL secret with your custom password
oc create secret generic postgresql-secret \
  --from-literal=database-user=demo \
  --from-literal=database-password="$DB_PASSWORD" \
  --from-literal=database-name=demodb \
  --from-literal=database-url="postgresql://demo:$DB_PASSWORD@postgresql:5432/demodb"

# Deploy PostgreSQL
oc apply -f openshift/postgresql.yaml
```

### Verify PostgreSQL Deployment

Wait for PostgreSQL to be ready, then verify the connection:

```bash
# Check PostgreSQL pod is running
oc get pods -l app=postgresql

# Test database connection (should show "demo" database exists)
oc exec -it deployment/postgresql -- psql -U demo -d demodb -c "\l"

# Test database connectivity with your credentials
oc exec -it deployment/postgresql -- psql -U demo -d demodb -c "SELECT version();"
```

If the verification commands fail, check the logs:
```bash
# Check PostgreSQL logs for connection issues
oc logs deployment/postgresql

# Verify secret was created correctly
oc get secret postgresql-secret -o yaml
```

### Common Issues and Solutions

**PostgreSQL pod not starting:**
```bash
# Check pod status and events
oc describe pod -l app=postgresql
oc get events --field-selector involvedObject.kind=Pod
```

**Authentication failed:**
```bash
# Verify your password was set correctly in the secret
oc get secret postgresql-secret -o jsonpath='{.data.database-password}' | base64 -d && echo

# Re-create the secret if password is incorrect
oc delete secret postgresql-secret
export DB_PASSWORD="your_correct_password" # pragma: allowlist secret
oc create secret generic postgresql-secret \
  --from-literal=database-user=demo \
  --from-literal=database-password="$DB_PASSWORD" \
  --from-literal=database-name=demodb \
  --from-literal=database-url="postgresql://demo:$DB_PASSWORD@postgresql:5432/demodb"
```

**Connection timeout:**
```bash
# Check if PostgreSQL service is available
oc get svc postgresql
oc get endpoints postgresql

# Test internal connectivity from another pod
oc run test-pod --image=postgres:15 --rm -it --restart=Never -- psql "postgresql://demo:$DB_PASSWORD@postgresql:5432/demodb" -c "SELECT 1;"
```

## OpenShift Resources

### PostgreSQL Deployment
- **Secret**: Database credentials (demo/YOUR_UNIQUE_PASSWORD)
- **PVC**: 1GB persistent volume for database storage
- **Deployment**: PostgreSQL 15 container with resource limits
- **Service**: Internal database service on port 5432

### V2 App Deployment  
- **Deployment**: App container with DATABASE_URL environment variable
- **Service**: HTTP service on port 8080
- **Route**: Secure HTTPS route with edge TLS termination
- **BuildConfig**: Builds app image from GitHub Dockerfile
