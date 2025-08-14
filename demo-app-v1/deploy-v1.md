# Demo App V1 Deployment Guide

## OpenShift Deployment with Resource Limits

This guide deploys the Demo App V1 with proper CPU and memory limits to demonstrate container resource management.

### Resource Configuration
- **CPU Request**: 100m (0.1 cores)
- **CPU Limit**: 500m (0.5 cores)  
- **Memory Request**: 128Mi
- **Memory Limit**: 256Mi

### Deployment Steps

1. **Create/Apply BuildConfig and ImageStream**:
   ```bash
   oc apply -f openshift/buildconfig.yaml
   ```

2. **Start the Build** (if using Git source):
   ```bash
   oc start-build openshift-demo-app-v1
   ```

   Or for local source:
   ```bash
   oc start-build openshift-demo-app-v1 --from-dir=. --follow
   ```

3. **Deploy the Application**:
   ```bash
   oc apply -f openshift/app-v1.yaml
   ```

4. **Get the Route URL**:
   ```bash
   oc get route openshift-demo-app-v1
   ```

### Alternative: Direct S2I Build and Deploy

For quick deployment from local source:

```bash
# Create new app with resource limits
oc new-app python:3.11~. --name=openshift-demo-app-v1 \
  --labels=app=openshift-demo-app-v1,version=v1

# Apply resource limits
oc patch dc/openshift-demo-app-v1 -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "openshift-demo-app-v1",
          "resources": {
            "requests": {"cpu": "100m", "memory": "128Mi"},
            "limits": {"cpu": "500m", "memory": "256Mi"}
          }
        }]
      }
    }
  }
}'

# Expose the service
oc expose svc/openshift-demo-app-v1

# Enable TLS
oc patch route/openshift-demo-app-v1 -p '{
  "spec": {
    "tls": {
      "termination": "edge",
      "insecureEdgeTerminationPolicy": "Redirect"
    }
  }
}'
```

### Verification

1. **Check Pod Resource Limits**:
   ```bash
   oc describe pod -l app=openshift-demo-app-v1
   ```

2. **View Resource Usage**:
   ```bash
   oc adm top pod -l app=openshift-demo-app-v1
   ```

3. **Access the Application**:
   - Navigate to the route URL
   - Check the "Metrics" section for real-time resource monitoring
   - Verify CPU and memory limits are displayed correctly

### Expected Metrics Display

With proper resource limits, the metrics should show:
- **CPU Utilization**: X% / 0.5 cores
- **CPU vs Limit**: X% (actual usage vs 500m limit)  
- **RAM Utilization**: X% (usage/256 MB)
- **RAM vs Limit**: X% (usage vs 256Mi limit)

### Scaling for Demo

To demonstrate horizontal scaling:
```bash
# Scale to 3 replicas
oc scale dc/openshift-demo-app-v1 --replicas=3

# Generate traffic to see resource usage
curl -X POST "https://your-route/api/persistence/test" \
  -H "Content-Type: application/json" \
  -d '{"data": "load test"}'
```

### Resource Monitoring Commands

- **Real-time pod metrics**: `oc adm top pod -l app=openshift-demo-app-v1`
- **Resource quotas**: `oc describe quota`
- **Pod resource specs**: `oc get pod -l app=openshift-demo-app-v1 -o jsonpath='{.items[0].spec.containers[0].resources}'`