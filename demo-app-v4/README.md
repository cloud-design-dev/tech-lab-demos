# Demo App V4: OpenShift Health Probes & Application Readiness

This version of the demo application focuses on **health probe configuration** using the `oc` CLI tool and demonstrates **application lifecycle management** concepts in OpenShift.

## Overview

Demo App V4 builds upon the resource management features of V3 and adds:
- **Health probe detection** and status monitoring
- **Step 6 completion workflow** based on probe configuration
- **Multiple probe configuration methods** using YAML files and CLI commands
- **Production-ready health checks** for container orchestration

## Prerequisites

Before deploying, ensure you have:

```bash
# Verify OpenShift CLI access
oc whoami
oc project

# Check cluster access
oc get nodes

# Verify you're in the correct project/namespace
oc project demo-lab-apps  # or your target namespace
```

## Step-by-Step Deployment

### 1. Deploy PostgreSQL Database (if not already deployed)

```bash
# Deploy PostgreSQL with persistent storage
oc apply -f openshift/postgresql.yaml

# Verify PostgreSQL deployment
oc get pods -l app=postgresql
oc get pvc postgresql-storage

# Check PostgreSQL is ready
oc logs deployment/postgresql
```

### 2. Build and Deploy the Application

```bash
# Create the build configuration and image stream
oc apply -f openshift/buildconfig.yaml

# Start the initial build from source
oc start-build demo-app-v4 --follow

# Verify the build completed
oc get builds
oc get imagestream demo-app-v4
```

### 3. Deploy the Application (Without Health Probes)

```bash
# Deploy the application with resource limits but NO health probes
oc apply -f openshift/deployment.yaml

# Create the service
oc apply -f openshift/service.yaml

# Create the external route
oc apply -f openshift/route.yaml

# Verify deployment
oc get deployment demo-app-v4
oc get pods -l app=demo-app-v4
```

### 4. Access the Application & Verify Missing Probes

```bash
# Get the application URL
oc get route demo-app-v4 -o jsonpath='{.spec.host}'

# Or use this one-liner to open in browser
open "https://$(oc get route demo-app-v4 -o jsonpath='{.spec.host}')"
```

**Expected Behavior:**
- Navigate to the deployed application
- **Step 6 card** will show "Health Probes: Not Configured"
- The application will detect missing probes and remain incomplete
- This demonstrates the importance of health checks in production

## Health Probe Configuration Workflow

### Method 1: YAML File Configuration (Recommended)

Create a health probes configuration file:

```bash
# Create probes configuration file
cat > health-probes.yaml << 'EOF'
spec:
  template:
    spec:
      containers:
      - name: demo-app-v4
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /api/ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        startupProbe:
          httpGet:
            path: /api/health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 30
EOF

# Apply the probes to the existing deployment
oc patch deployment demo-app-v4 --patch-file health-probes.yaml
```

### Method 2: Direct oc patch Commands

```bash
# Add liveness probe
oc patch deployment demo-app-v4 -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "demo-app-v4",
          "livenessProbe": {
            "httpGet": {
              "path": "/api/health",
              "port": 8080
            },
            "initialDelaySeconds": 30,
            "periodSeconds": 10,
            "timeoutSeconds": 5,
            "failureThreshold": 3
          }
        }]
      }
    }
  }
}'

# Add readiness probe
oc patch deployment demo-app-v4 -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "demo-app-v4",
          "readinessProbe": {
            "httpGet": {
              "path": "/api/ready",
              "port": 8080
            },
            "initialDelaySeconds": 5,
            "periodSeconds": 5,
            "timeoutSeconds": 3,
            "failureThreshold": 3
          }
        }]
      }
    }
  }
}'

# Add startup probe
oc patch deployment demo-app-v4 -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "demo-app-v4",
          "startupProbe": {
            "httpGet": {
              "path": "/api/health",
              "port": 8080
            },
            "initialDelaySeconds": 10,
            "periodSeconds": 5,
            "timeoutSeconds": 3,
            "failureThreshold": 30
          }
        }]
      }
    }
  }
}'
```

### Method 3: Complete Deployment Replacement

```bash
# Create a complete deployment with probes
cat > deployment-with-probes.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-app-v4
  labels:
    app: demo-app-v4
    version: v4
spec:
  replicas: 2
  selector:
    matchLabels:
      app: demo-app-v4
  template:
    metadata:
      labels:
        app: demo-app-v4
        version: v4
    spec:
      containers:
      - name: demo-app-v4
        image: demo-app-v4:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: postgresql-secret
              key: database_url
              optional: true
        - name: POSTGRES_HOST
          value: postgresql
        - name: POSTGRES_DB
          value: demo_app_v4
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgresql-secret
              key: username
              optional: true
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgresql-secret
              key: password
              optional: true
        resources:
          requests:
            cpu: 50m
            memory: 64Mi
          limits:
            cpu: 200m
            memory: 128Mi
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /api/ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        startupProbe:
          httpGet:
            path: /api/health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 30
  triggers:
  - type: ImageChange
    imageChangeParams:
      automatic: true
      containerNames:
      - demo-app-v4
      from:
        kind: ImageStreamTag
        name: demo-app-v4:latest
EOF

# Replace the existing deployment
oc replace -f deployment-with-probes.yaml
```

## Verification & Step 6 Completion

### 1. Verify Probe Configuration

```bash
# Check deployment probe configuration
oc describe deployment demo-app-v4 | grep -A 10 "Liveness:\|Readiness:\|Startup:"

# View probe details in JSON format
oc get deployment demo-app-v4 -o jsonpath='{.spec.template.spec.containers[0].livenessProbe}'
oc get deployment demo-app-v4 -o jsonpath='{.spec.template.spec.containers[0].readinessProbe}'
oc get deployment demo-app-v4 -o jsonpath='{.spec.template.spec.containers[0].startupProbe}'
```

### 2. Monitor Pod Health

```bash
# Check pod status and probe results
oc get pods -l app=demo-app-v4
oc describe pods -l app=demo-app-v4

# View probe events
oc get events --field-selector reason=Unhealthy,reason=ProbeWarning --sort-by='.firstTimestamp'

# Monitor real-time pod events
oc get events --watch --field-selector involvedObject.kind=Pod
```

### 3. Application Step 6 Completion

Once probes are configured:

1. **Refresh the application page** - the probe detection runs automatically
2. **Step 6 card updates** to show "Health Probes: Configured ✓"
3. **Step completion** happens automatically when all three probes are detected
4. **Celebration UI** appears showing successful completion

Expected API response after configuration:
```json
{
  "step_6_complete": true,
  "probes": {
    "liveness": {"configured": true, "endpoint": "/api/health"},
    "readiness": {"configured": true, "endpoint": "/api/ready"}, 
    "startup": {"configured": true, "endpoint": "/api/health"}
  },
  "message": "All health probes configured successfully"
}
```

## Key OpenShift/Kubernetes Concepts

### Health Probe Types

#### Liveness Probe
```yaml
livenessProbe:
  httpGet:
    path: /api/health
    port: 8080
  initialDelaySeconds: 30    # Wait 30s before first check
  periodSeconds: 10          # Check every 10s
  timeoutSeconds: 5          # 5s timeout per check
  failureThreshold: 3        # Restart after 3 failures
```

**Purpose:** Determines if container should be restarted
- **Failure Action:** Pod restart
- **Use Case:** Detect application deadlocks or unrecoverable errors

#### Readiness Probe
```yaml
readinessProbe:
  httpGet:
    path: /api/ready
    port: 8080
  initialDelaySeconds: 5     # Quick first check
  periodSeconds: 5           # Frequent checks
  timeoutSeconds: 3          # Fast timeout
  failureThreshold: 3        # Remove from service after 3 failures
```

**Purpose:** Determines if container can accept traffic
- **Failure Action:** Remove from service load balancing
- **Use Case:** Database connections not ready, dependencies unavailable

#### Startup Probe
```yaml
startupProbe:
  httpGet:
    path: /api/health
    port: 8080
  initialDelaySeconds: 10    # Initial startup delay
  periodSeconds: 5           # Check every 5s during startup
  timeoutSeconds: 3          # Fast response expected
  failureThreshold: 30       # Allow up to 150s total startup time
```

**Purpose:** Handles slow-starting containers
- **Behavior:** Disables liveness/readiness until startup succeeds
- **Use Case:** Applications with long initialization periods

### Health Endpoint Implementation

The V4 application provides three health endpoints:

#### `/api/health` - Liveness/Startup Endpoint
```bash
curl -i https://$(oc get route demo-app-v4 -o jsonpath='{.spec.host}')/api/health

# Expected Response:
HTTP/1.1 200 OK
{
  "status": "healthy",
  "timestamp": "2025-01-09T15:30:45.123456",
  "database": "connected",
  "app_version": "v4"
}
```

#### `/api/ready` - Readiness Endpoint  
```bash
curl -i https://$(oc get route demo-app-v4 -o jsonpath='{.spec.host}')/api/ready

# Expected Response:
HTTP/1.1 200 OK
{
  "status": "ready",
  "database_connection": true,
  "dependencies": "available",
  "ready_for_traffic": true
}
```

#### `/api/probe-status` - Probe Configuration Status
```bash
curl https://$(oc get route demo-app-v4 -o jsonpath='{.spec.host}')/api/probe-status

# Response shows current probe configuration:
{
  "step_6_complete": true,
  "probes": {
    "liveness": {"configured": true, "endpoint": "/api/health"},
    "readiness": {"configured": true, "endpoint": "/api/ready"},
    "startup": {"configured": true, "endpoint": "/api/health"}
  }
}
```

## Demonstration Scenarios

### 1. Missing Probes Detection

```bash
# Deploy application without probes
oc apply -f openshift/deployment.yaml

# Verify no probes configured
oc describe deployment demo-app-v4 | grep -i probe
# Should show: No probes configured

# Check application Step 6 status
curl https://$(oc get route demo-app-v4 -o jsonpath='{.spec.host}')/api/probe-status
# Shows: "step_6_complete": false
```

### 2. Probe Configuration Process

```bash
# Configure probes using YAML method
oc patch deployment demo-app-v4 --patch-file health-probes.yaml

# Monitor rollout of new pods with probes
oc rollout status deployment/demo-app-v4

# Verify probe configuration
oc describe deployment demo-app-v4 | grep -A 5 "Liveness:\|Readiness:\|Startup:"

# Confirm Step 6 completion
curl https://$(oc get route demo-app-v4 -o jsonpath='{.spec.host}')/api/probe-status
# Shows: "step_6_complete": true
```

### 3. Probe Failure Simulation

```bash
# Simulate application failure (breaks liveness probe)
curl -X POST https://$(oc get route demo-app-v4 -o jsonpath='{.spec.host}')/api/simulate-failure

# Watch for pod restart due to liveness probe failure
oc get pods -l app=demo-app-v4 -w

# View probe failure events
oc get events --field-selector reason=Unhealthy --sort-by='.firstTimestamp'
```

### 4. Database Dependency Testing

```bash
# Simulate database connection issues (affects readiness)
oc scale deployment postgresql --replicas=0

# Watch pods become not ready (removed from service)
oc get pods -l app=demo-app-v4 -w

# Readiness probe should fail, but liveness should pass
curl -i https://$(oc get route demo-app-v4 -o jsonpath='{.spec.host}')/api/ready
# Should return 503 Service Unavailable

# Restore database
oc scale deployment postgresql --replicas=1
```

## Troubleshooting

### Common Issues

#### Probe Endpoints Returning 404
```bash
# Verify health endpoints are available
oc rsh deployment/demo-app-v4
curl localhost:8080/api/health
curl localhost:8080/api/ready

# Check application logs for endpoint issues
oc logs -f deployment/demo-app-v4
```

#### Probe Timeouts
```bash
# Check current timeout settings
oc get deployment demo-app-v4 -o jsonpath='{.spec.template.spec.containers[0].livenessProbe.timeoutSeconds}'

# Increase timeout if needed
oc patch deployment demo-app-v4 -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "demo-app-v4",
          "livenessProbe": {
            "timeoutSeconds": 10
          }
        }]
      }
    }
  }
}'
```

#### Startup Probe Taking Too Long
```bash
# Check startup probe configuration
oc describe deployment demo-app-v4 | grep -A 10 "Startup:"

# Calculate total startup time allowed
# failureThreshold * periodSeconds = maximum startup time
# Example: 30 * 5 = 150 seconds maximum

# Increase failure threshold if needed
oc patch deployment demo-app-v4 -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "demo-app-v4", 
          "startupProbe": {
            "failureThreshold": 60
          }
        }]
      }
    }
  }
}'
```

#### Pods Stuck in Not Ready State
```bash
# Check readiness probe status
oc describe pods -l app=demo-app-v4 | grep -A 20 "Conditions:"

# Test readiness endpoint manually
oc port-forward deployment/demo-app-v4 8080:8080 &
curl localhost:8080/api/ready

# Check for database connectivity issues
oc logs deployment/demo-app-v4 | grep -i database
```

### Probe Configuration Verification

```bash
# Complete probe configuration check
oc get deployment demo-app-v4 -o yaml | grep -A 20 "livenessProbe:\|readinessProbe:\|startupProbe:"

# Verify all three probe types are configured
oc get deployment demo-app-v4 -o jsonpath='{.spec.template.spec.containers[0]}' | jq '.livenessProbe, .readinessProbe, .startupProbe'

# Check probe endpoints are responding
for endpoint in health ready; do
  echo "Testing /$endpoint:"
  curl -i https://$(oc get route demo-app-v4 -o jsonpath='{.spec.host}')/api/$endpoint
  echo
done
```

## Advanced Operations

### Probe Tuning for Different Environments

#### Development Environment (Fast Feedback)
```bash
# Quick probe configuration for development
oc patch deployment demo-app-v4 -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "demo-app-v4",
          "livenessProbe": {
            "initialDelaySeconds": 10,
            "periodSeconds": 5,
            "timeoutSeconds": 2,
            "failureThreshold": 2
          },
          "readinessProbe": {
            "initialDelaySeconds": 2,
            "periodSeconds": 2,
            "timeoutSeconds": 1,
            "failureThreshold": 2
          }
        }]
      }
    }
  }
}'
```

#### Production Environment (Stable)
```bash
# Conservative probe configuration for production
oc patch deployment demo-app-v4 -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "demo-app-v4",
          "livenessProbe": {
            "initialDelaySeconds": 60,
            "periodSeconds": 30,
            "timeoutSeconds": 10,
            "failureThreshold": 5
          },
          "readinessProbe": {
            "initialDelaySeconds": 10,
            "periodSeconds": 10,
            "timeoutSeconds": 5,
            "failureThreshold": 3
          }
        }]
      }
    }
  }
}'
```

### Probe Monitoring and Alerting

```bash
# Set up probe failure monitoring
oc get events --field-selector reason=Unhealthy,reason=ProbeWarning -o wide --sort-by='.firstTimestamp'

# Create a script to monitor probe health
cat > monitor-probes.sh << 'EOF'
#!/bin/bash
while true; do
  echo "=== $(date) ==="
  echo "Pod Status:"
  oc get pods -l app=demo-app-v4 -o custom-columns=NAME:.metadata.name,READY:.status.conditions[?@.type==\"Ready\"].status,STATUS:.status.phase
  
  echo -e "\nRecent Probe Events:"
  oc get events --field-selector reason=Unhealthy,reason=ProbeWarning --sort-by='.firstTimestamp' --no-headers | tail -5
  
  sleep 30
done
EOF

chmod +x monitor-probes.sh
./monitor-probes.sh
```

### Rolling Updates with Health Checks

```bash
# Configure rolling update strategy with health checks
oc patch deployment demo-app-v4 -p '{
  "spec": {
    "strategy": {
      "type": "RollingUpdate",
      "rollingUpdate": {
        "maxSurge": 1,
        "maxUnavailable": 0
      }
    }
  }
}'

# Perform rolling update and monitor health
oc set image deployment/demo-app-v4 demo-app-v4=demo-app-v4:latest
oc rollout status deployment/demo-app-v4 --watch=true

# Verify health during rollout
watch 'oc get pods -l app=demo-app-v4; echo; oc get events --field-selector reason=Unhealthy --no-headers | tail -3'
```

## Cleanup

```bash
# Remove all V4 resources
oc delete -f openshift/

# Or remove individually
oc delete deployment,service,route,buildconfig,imagestream -l app=demo-app-v4

# Keep PostgreSQL for other demo versions
# oc delete -f openshift/postgresql.yaml  # Only if needed

# Clean up probe configuration files
rm -f health-probes.yaml deployment-with-probes.yaml monitor-probes.sh
```

## Key Learning Outcomes

After completing this demo, users will understand:

1. **Health Probe Configuration**: Liveness, readiness, and startup probe setup
2. **Container Lifecycle Management**: How probes affect pod lifecycle and traffic routing
3. **Production Readiness**: Critical health checks for containerized applications  
4. **Probe Tuning**: Balancing responsiveness with stability across environments
5. **Troubleshooting**: Debugging probe failures and configuration issues
6. **OpenShift CLI Mastery**: Multiple methods for configuring and managing probes
7. **Application Monitoring**: Real-time probe status and failure detection

This demo provides comprehensive hands-on experience with production-ready health checks while demonstrating the progression from basic deployment to fully monitored, self-healing applications in OpenShift.