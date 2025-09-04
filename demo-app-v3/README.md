# Demo App V3: Resource Management & Auto-Scaling

Version 3 of the OpenShift demo application focuses on **resource management**, **health monitoring**, and **horizontal pod autoscaling**. This application demonstrates production-ready container orchestration with proper resource limits, health checks, and automatic scaling based on CPU/memory utilization.

## Architecture Overview

**Demo App V3** builds upon V1 (ephemeral) and V2 (persistent) by adding:
- **Resource Limits**: CPU and memory constraints with configurable limits
- **Health Checks**: Comprehensive liveness and readiness probes
- **Horizontal Pod Autoscaling (HPA)**: Automatic scaling based on resource utilization
- **Load Testing**: Built-in traffic generation for scaling demonstrations
- **Resource Monitoring**: Real-time CPU/memory usage vs limits visualization

## Key Features

### Resource Management
- **CPU Requests/Limits**: Configurable CPU allocation and maximum usage
- **Memory Requests/Limits**: Memory allocation with container boundaries
- **Resource Monitoring**: Real-time utilization vs limits display
- **Constraint Enforcement**: Demonstration of throttling and OOM scenarios

### Health & Monitoring
- **Liveness Probes**: Container restart automation on failure
- **Readiness Probes**: Traffic routing based on application readiness
- **Startup Probes**: Graceful application initialization handling
- **Metrics Endpoints**: Prometheus-compatible resource metrics

### Auto-Scaling
- **Horizontal Pod Autoscaler**: CPU and memory-based scaling triggers
- **Traffic Generation**: Built-in load testing for scaling demonstrations
- **Scale Events**: Visual feedback on pod creation/termination
- **Performance Metrics**: Request rate and response time tracking

## Deployment Guide

### Prerequisites
- OpenShift cluster with metrics server enabled
- `oc` CLI configured and authenticated
- Cluster admin privileges for HPA configuration

### Quick Deployment

```bash
# Clone and navigate to V3
git clone <repository>
cd tech-lab-demos/demo-app-v3

# Deploy with resource limits and HPA
oc apply -f openshift/

# Verify deployment
oc get deployment,hpa,pod -l app=demo-app-v3
```

### Step-by-Step Deployment

#### 1. Create Application Deployment
```bash
# Deploy application with resource limits
oc apply -f openshift/deployment.yaml

# Verify resource limits are applied
oc describe deployment demo-app-v3 | grep -A 10 'Limits:'
```

#### 2. Configure Health Checks
```bash
# Health checks are included in deployment.yaml
# Verify probe configuration
oc describe pod -l app=demo-app-v3 | grep -A 5 'Liveness:'
oc describe pod -l app=demo-app-v3 | grep -A 5 'Readiness:'
```

#### 3. Create Service and Route
```bash
# Deploy service and external route
oc apply -f openshift/service.yaml
oc apply -f openshift/route.yaml

# Get application URL
oc get route demo-app-v3 -o jsonpath='{.spec.host}'
```

#### 4. Configure Horizontal Pod Autoscaler
```bash
# Deploy HPA with CPU/memory targets
oc apply -f openshift/hpa.yaml

# Verify HPA configuration
oc describe hpa demo-app-v3
```

## Resource Configuration

### CPU & Memory Limits

The application uses the following resource configuration:

```yaml
resources:
  requests:
    cpu: 100m      # 0.1 CPU cores minimum
    memory: 128Mi  # 128MB minimum memory
  limits:
    cpu: 500m      # 0.5 CPU cores maximum
    memory: 256Mi  # 256MB maximum memory
```

### Health Check Configuration

#### Liveness Probe
```yaml
livenessProbe:
  httpGet:
    path: /api/health
    port: 5000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

#### Readiness Probe  
```yaml
readinessProbe:
  httpGet:
    path: /api/ready
    port: 5000
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2
```

#### Startup Probe
```yaml
startupProbe:
  httpGet:
    path: /api/startup
    port: 5000
  initialDelaySeconds: 10
  periodSeconds: 5
  failureThreshold: 10
```

## Horizontal Pod Autoscaling

### HPA Configuration

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: demo-app-v3-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: demo-app-v3
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Scaling Triggers
- **CPU Utilization**: Scales when average CPU > 70%
- **Memory Utilization**: Scales when average memory > 80%
- **Min Replicas**: 2 (high availability)
- **Max Replicas**: 10 (resource protection)

## Load Testing & Scaling Demo

### Generate Load for Scaling
```bash
# Start load testing from application UI
curl -X POST http://<app-url>/api/load-test \
  -H "Content-Type: application/json" \
  -d '{"duration": 300, "rps": 50, "cpu_intensive": true}'

# Monitor HPA scaling decisions
watch oc get hpa demo-app-v3

# Watch pod scaling events
oc get events --field-selector type=Normal --sort-by='.firstTimestamp'
```

### Monitor Resource Utilization
```bash
# View real-time pod resources
oc adm top pod -l app=demo-app-v3

# Check HPA status and metrics
oc describe hpa demo-app-v3

# Monitor scaling events
oc get events --field-selector reason=SuccessfulRescale
```

## API Endpoints

### Health & Status
- `GET /api/health` - Liveness probe endpoint
- `GET /api/ready` - Readiness probe endpoint  
- `GET /api/startup` - Startup probe endpoint
- `GET /api/metrics` - Prometheus metrics

### Resource Monitoring
- `GET /api/resources` - Current CPU/memory usage vs limits
- `GET /api/pod-info` - Pod metadata and resource specifications
- `GET /api/scaling-events` - Recent HPA scaling activities

### Load Generation
- `POST /api/load-test` - Generate CPU/memory load for scaling
- `GET /api/load-status` - Current load testing status
- `DELETE /api/load-test` - Stop active load testing

## Demonstration Scenarios

### 1. Resource Limit Enforcement
```bash
# Generate high CPU load
curl -X POST http://<app-url>/api/load-test \
  -d '{"cpu_intensive": true, "duration": 120}'

# Observe CPU throttling at 500m limit
oc adm top pod -l app=demo-app-v3
```

### 2. Health Check Automation
```bash
# Simulate application failure
curl -X POST http://<app-url>/api/simulate-failure

# Watch pod restart via liveness probe
oc get pod -l app=demo-app-v3 -w
```

### 3. Auto-Scaling Demonstration
```bash
# Start sustained load
curl -X POST http://<app-url>/api/load-test \
  -d '{"duration": 600, "rps": 100, "cpu_intensive": true}'

# Monitor HPA scaling up
watch oc get hpa,pod -l app=demo-app-v3

# Stop load and watch scale down
curl -X DELETE http://<app-url>/api/load-test
```

## Troubleshooting

### HPA Not Scaling
```bash
# Check metrics server
oc get apiservice v1beta1.metrics.k8s.io

# Verify resource metrics
oc adm top pod -l app=demo-app-v3

# Check HPA events
oc describe hpa demo-app-v3 | grep Events -A 10
```

### Pod Not Starting
```bash
# Check startup probe
oc describe pod -l app=demo-app-v3 | grep -A 5 'Startup:'

# View pod events
oc describe pod -l app=demo-app-v3 | grep Events -A 10
```

### Resource Constraints
```bash
# Check actual vs requested resources
oc describe pod -l app=demo-app-v3 | grep -A 10 'Requests:'

# Monitor resource usage
oc adm top pod -l app=demo-app-v3 --containers
```

## Cleanup

```bash
# Remove all V3 resources
oc delete -f openshift/

# Verify cleanup
oc get deployment,service,route,hpa -l app=demo-app-v3
```

---

**Demo App V3** provides a complete platform for demonstrating enterprise container orchestration concepts including resource management, health monitoring, and automatic scaling in OpenShift environments.