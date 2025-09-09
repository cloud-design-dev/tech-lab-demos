# Demo App V3: OpenShift CLI & Resource Management

This version of the demo application focuses on **command-line deployment** using the `oc` CLI tool and demonstrates **resource management** and **horizontal pod autoscaling** concepts in OpenShift.

## Overview

Demo App V3 builds upon the persistence features of V2 and adds:
- **Aggressive resource limits** for faster scaling demonstrations
- **Built-in load testing** to trigger HPA scaling
- **Real-time resource monitoring** with CPU/memory vs limits
- **CLI-focused deployment** using `oc` commands

## Prerequisites

> needs fix

- Launch Cloud Shell: https://cloud.ibm.com/shell
- list clusters with `ibmcloud oc clusters`
- configure cluster with admin flag: `ibmcloud oc cluster config --cluster CLUSTER_NAME --admin`

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
oc start-build demo-app-v3 --follow

# Verify the build completed
oc get builds
oc get imagestream demo-app-v3
```

### 3. Deploy the Application

```bash
# Deploy the application with resource limits
oc apply -f openshift/deployment.yaml

# Create the service
oc apply -f openshift/service.yaml

# Create the external route
oc apply -f openshift/route.yaml

# Verify deployment
oc get deployment demo-app-v3
oc get pods -l app=demo-app-v3
```

### 4. Configure Horizontal Pod Autoscaler

```bash
# Deploy HPA for automatic scaling
oc apply -f openshift/hpa.yaml

# Verify HPA configuration
oc get hpa demo-app-v3
oc describe hpa demo-app-v3

# Check current resource utilization
oc adm top pods -l app=demo-app-v3
```

### 5. Access the Application

```bash
# Get the application URL
oc get route demo-app-v3 -o jsonpath='{.spec.host}'

# Or use this one-liner to open in browser
open "https://$(oc get route demo-app-v3 -o jsonpath='{.spec.host}')"
```

## Key OpenShift/Kubernetes Concepts

### Resource Management

This demo showcases several resource management concepts:

#### Resource Requests & Limits
```yaml
resources:
  limits:
    cpu: 200m        # Maximum CPU (0.2 cores)
    memory: 128Mi    # Maximum memory
  requests:
    cpu: 50m         # Guaranteed CPU (0.05 cores)
    memory: 64Mi     # Guaranteed memory
```

**Key Concepts:**
- **Requests**: Guaranteed resources for scheduling
- **Limits**: Maximum resources before throttling/termination
- **CPU**: Measured in millicores (1000m = 1 core)
- **Memory**: Measured in bytes (Mi = Mebibytes)

#### Horizontal Pod Autoscaler (HPA)

```bash
# View HPA status
oc get hpa demo-app-v3

# Expected output:
NAME          REFERENCE                TARGETS                        MINPODS   MAXPODS   REPLICAS   AGE
demo-app-v3   Deployment/demo-app-v3   cpu: 15%/50%, memory: 45%/60%   2         8         4          10m
```

**HPA Configuration:**
- **CPU Target**: 50% average utilization
- **Memory Target**: 60% average utilization  
- **Min Replicas**: 2 (high availability)
- **Max Replicas**: 8 (cost control)
- **Scale Up**: Aggressive (30s window, up to 4 pods at once)
- **Scale Down**: Conservative (180s stabilization)

### Container Image Management

#### Source-to-Image (S2I) Build Process

```bash
# View build configuration
oc describe buildconfig demo-app-v3

# Manual build trigger
oc start-build demo-app-v3

# Follow build logs
oc logs -f buildconfig/demo-app-v3
```

**S2I Process:**
1. **Git Source**: Pulls code from GitHub repository
2. **Builder Image**: Uses Python 3.9 UBI base image
3. **Build Process**: Installs dependencies, copies code
4. **Output Image**: Creates application image in ImageStream
5. **Auto Deployment**: Triggers rollout when image updates

#### ImageStream Integration

```bash
# View ImageStream
oc get imagestream demo-app-v3

# Check image history
oc describe imagestream demo-app-v3

# Tag specific image versions
oc tag demo-app-v3:latest demo-app-v3:stable
```

**ImageStream Benefits:**
- **Local Registry**: Images stored in OpenShift registry
- **Automatic Updates**: Deployments update when images change
- **Image Security**: Built-in vulnerability scanning
- **Rollback Support**: Previous image versions retained

### Networking & Services

#### Service Configuration
```yaml
apiVersion: v1
kind: Service
metadata:
  name: demo-app-v3
spec:
  selector:
    app: demo-app-v3
  ports:
  - port: 8080
    targetPort: 8080
```

#### Route Configuration
```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: demo-app-v3
spec:
  tls:
    termination: edge    # SSL termination at route level
  to:
    kind: Service
    name: demo-app-v3
```

**Networking Concepts:**
- **Service**: Internal load balancer for pods
- **Route**: External HTTPS access with SSL termination
- **Selectors**: Label-based pod targeting
- **Load Balancing**: Automatic traffic distribution

## Demonstration Scenarios

### 1. Resource Limit Testing

```bash
# Start load test via application UI or API
curl -X POST "https://$(oc get route demo-app-v3 -o jsonpath='{.spec.host}')/api/load-test" \
  -H "Content-Type: application/json" \
  -d '{"duration": 120, "cpu_intensive": true}'

# Monitor resource utilization
watch oc adm top pods -l app=demo-app-v3

# Expected: CPU usage should hit ~100% quickly due to low limits
```

### 2. HPA Scaling Demonstration

```bash
# Monitor HPA in real-time
watch oc get hpa demo-app-v3

# Watch pod scaling
watch oc get pods -l app=demo-app-v3

# View scaling events
oc get events --field-selector reason=SuccessfulRescale --sort-by='.firstTimestamp'
```

**Expected Timeline:**
- **0-30s**: Load test starts, CPU spikes to 100%+
- **30-60s**: HPA detects high utilization, scales to 4 pods
- **60-90s**: Further scaling if load continues
- **2-3min after load stops**: Gradual scale down begins

### 3. Application Updates

```bash
# Update application code and rebuild
git commit -am "Update application"
git push origin main

# Manual rebuild and deploy
oc start-build demo-app-v3 --follow
oc rollout restart deployment/demo-app-v3

# Monitor rollout
oc rollout status deployment/demo-app-v3

# Verify all pods updated
oc get pods -l app=demo-app-v3 -o wide
```

## Troubleshooting

### Common Issues

#### Build Failures
```bash
# Check build logs
oc logs -f buildconfig/demo-app-v3

# Common solutions:
oc delete build --all -l buildconfig=demo-app-v3
oc start-build demo-app-v3
```

#### Pod Startup Issues
```bash
# Check pod status
oc describe pods -l app=demo-app-v3

# View application logs
oc logs -f deployment/demo-app-v3

# Common issues:
# - Database connection failures
# - Resource limit exceeded
# - Image pull errors
```

#### HPA Not Scaling
```bash
# Verify metrics server
oc get apiservice v1beta1.metrics.k8s.io

# Check HPA conditions
oc describe hpa demo-app-v3 | grep -A 10 "Conditions:"

# Verify resource metrics
oc adm top pods -l app=demo-app-v3
```

#### Database Connection Issues
```bash
# Check PostgreSQL status
oc get pods -l app=postgresql
oc logs deployment/postgresql

# Verify secrets
oc get secret postgresql-secret
oc describe secret postgresql-secret

# Test database connectivity
oc rsh deployment/demo-app-v3
# Inside pod: curl localhost:8080/api/persistence/stats
```

## Advanced Operations

### Manual Scaling
```bash
# Scale to specific replica count
oc scale deployment demo-app-v3 --replicas=5

# Disable HPA temporarily
oc delete hpa demo-app-v3

# Re-enable HPA
oc apply -f openshift/hpa.yaml
```

### Resource Monitoring
```bash
# Real-time pod resources
oc adm top pods -l app=demo-app-v3 --containers

# Node resource utilization
oc adm top nodes

# Detailed resource usage
oc describe deployment demo-app-v3 | grep -A 10 "Limits:"
```

### Blue/Green Deployment
```bash
# Tag current version as stable
oc tag demo-app-v3:latest demo-app-v3:stable

# Deploy new version alongside current
oc new-app demo-app-v3:latest --name=demo-app-v3-new

# Switch traffic after validation
oc patch route demo-app-v3 -p '{"spec":{"to":{"name":"demo-app-v3-new"}}}'
```

## Cleanup

```bash
# Remove all V3 resources
oc delete -f openshift/

# Or remove individually
oc delete deployment,service,route,hpa,buildconfig,imagestream -l app=demo-app-v3

# Keep PostgreSQL for other demo versions
# oc delete -f openshift/postgresql.yaml  # Only if needed
```

## Key Learning Outcomes

After completing this demo, users will understand:

1. **OpenShift CLI Operations**: Build, deploy, scale, and manage applications
2. **Resource Management**: CPU/memory requests, limits, and utilization
3. **Auto-scaling**: HPA configuration and scaling behavior
4. **Container Builds**: S2I process and ImageStream management
5. **Networking**: Services, routes, and load balancing
6. **Monitoring**: Resource utilization and application metrics
7. **Troubleshooting**: Common issues and debugging techniques

This demo provides hands-on experience with production OpenShift concepts while maintaining educational simplicity.
