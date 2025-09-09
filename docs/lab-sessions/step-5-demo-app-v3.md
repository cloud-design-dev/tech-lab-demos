# Step 5: Deploy Demo App V3 (Resource Management & Auto-Scaling)

In this session, you'll deploy Demo App V3, which demonstrates advanced resource management and horizontal pod autoscaling (HPA). This step focuses heavily on `oc` command-line operations and production-ready scaling patterns.

!!! info "Estimated Time"
    **Setup Time:** 20-25 minutes  
    **Testing Time:** 15-20 minutes  
    **Load Testing:** 10-15 minutes

## 🎯 Learning Objectives

By the end of this step, you will:

- ✅ Configure resource requests and limits for production workloads
- ✅ Deploy and configure Horizontal Pod Autoscaler (HPA)
- ✅ Use `oc` commands for advanced application management
- ✅ Generate load to trigger automatic scaling events
- ✅ Monitor resource utilization and scaling behavior

## 📋 Prerequisites

Before starting this step:

- [ ] Completed [Step 4: Deploy Demo App V2](step-4-demo-app-v2.md)
- [ ] PostgreSQL database running from Step 4
- [ ] Comfortable with `oc` CLI commands
- [ ] Understanding of Kubernetes resource concepts

## 🏗️ Demo App V3 Overview

**Demo App V3** focuses on production-ready resource management and scaling:

### Key Features
- 📈 **Aggressive Resource Limits** to trigger scaling quickly
- ⚡ **Horizontal Pod Autoscaler** based on CPU and memory
- 🔧 **Built-in Load Testing** endpoints to generate traffic
- 📊 **Advanced Resource Monitoring** with real-time metrics
- 🎯 **Step 5 Highlighted** in the progress visualization

### Architecture
```mermaid
graph TB
    subgraph "Load Balancing"
        LB[Service Load Balancer]
    end
    
    subgraph "Auto Scaling"
        HPA[Horizontal Pod Autoscaler]
        HPA --> Metrics[Resource Metrics]
    end
    
    subgraph "Application Pods"
        Pod1[App Pod 1]
        Pod2[App Pod 2]
        Pod3[App Pod N]
    end
    
    subgraph "Shared Database"
        DB[(PostgreSQL)]
        PVC[Persistent Volume]
    end
    
    LB --> Pod1
    LB --> Pod2
    LB --> Pod3
    
    Metrics --> Pod1
    Metrics --> Pod2
    Metrics --> Pod3
    
    Pod1 --> DB
    Pod2 --> DB
    Pod3 --> DB
    DB --> PVC
    
    style HPA fill:#fff3e0
    style DB fill:#c8e6c9
    style PVC fill:#e3f2fd
```

## 📁 Step 1: Examine Demo App V3 Structure

First, let's explore the demo-app-v3 directory structure and understand the resource management setup.

### 1. Navigate to Demo App V3

```bash
# Change to the demo-app-v3 directory
cd tech-lab-demos/demo-app-v3

# Explore the application structure
ls -la

# Check the OpenShift deployment manifests
ls -la openshift/

# Review the README for specific deployment instructions
cat README.md
```

### 2. Examine the Resource Configuration

```bash
# Look at the deployment manifest
cat openshift/deployment.yaml

# Check the HPA configuration
cat openshift/hpa.yaml

# Review other OpenShift resources
ls openshift/*.yaml
```

## 🚀 Step 2: Deploy Demo App V3 with Resource Limits

We'll deploy V3 using the provided manifests with specific resource configurations.

### 1. Deploy All V3 Components

```bash
# Deploy all V3 components at once using the provided manifests
oc apply -f openshift/

# This creates:
# - BuildConfig and ImageStream
# - Deployment with resource limits
# - Service and Route
# - HorizontalPodAutoscaler
```

### 2. Alternative: Step-by-Step Deployment

If you want to understand each component:

```bash
# Deploy BuildConfig and ImageStream first
oc apply -f openshift/buildconfig.yaml
oc apply -f openshift/imagestream.yaml

# Start the build
oc start-build demoapp3 --follow

# Deploy the application with resource limits
oc apply -f openshift/deployment.yaml

# Create Service and Route
oc apply -f openshift/service.yaml
oc apply -f openshift/route.yaml
```

### 3. Monitor the Deployment

```bash
# Watch the build process
oc get builds -w

# Monitor deployment rollout
oc rollout status deployment/demoapp3 --timeout=300s

# Check pod status
oc get pods -l app=demoapp3
```

## 📈 Step 3: Configure Horizontal Pod Autoscaler

The HPA should already be deployed if you used `oc apply -f openshift/`. Let's verify and understand the configuration.

### 1. Verify HPA Deployment

```bash
# Check if HPA was created from the manifest
oc get hpa demoapp3-hpa

# If not created, deploy it manually
oc apply -f openshift/hpa.yaml
```

### 2. Examine HPA Configuration

```bash
# View the HPA configuration
oc describe hpa demoapp3-hpa

# Check the HPA manifest content
cat openshift/hpa.yaml
```

### 3. Monitor HPA Status

```bash
# Check HPA status
oc get hpa demoapp3-hpa

# Get detailed HPA information
oc describe hpa demoapp3-hpa

# Monitor HPA in real-time (keep this running in a separate terminal)
watch -n 5 'oc get hpa demoapp3-hpa'
```

## 🔍 Step 4: Monitor Initial State

### 1. Check Current Resource Usage

```bash
# View current pod resource usage
oc adm top pods -l app=demoapp3

# Check deployment status
oc get deployment demoapp3

# List all pods
oc get pods -l app=demoapp3 -o wide
```

### 2. Access the Application

```bash
# Get the application URL
APP_URL=$(oc get route demoapp3 -o jsonpath='{.spec.host}')
echo "Demo App V3 URL: https://$APP_URL"

# Test the application
curl -k https://$APP_URL/api/health
```

### 3. Explore V3-Specific Features

Visit the application in your browser and notice:
- **Step 5 highlighted** as current
- **Enhanced resource metrics** showing limits vs usage
- **Load testing controls** for triggering scaling
- **Multiple pod hostnames** if you refresh (load balancing)

## ⚡ Step 5: Load Testing and Scaling

### 1. Generate Load Using Built-in Endpoints

Demo App V3 includes load generation endpoints:

```bash
# Generate CPU load (in separate terminal)
while true; do 
  curl -k -s https://$APP_URL/api/load/cpu/5 > /dev/null
  sleep 1
done

# Generate memory load (in another terminal)  
while true; do
  curl -k -s https://$APP_URL/api/load/memory/50 > /dev/null
  sleep 2
done

# Generate traffic load (in another terminal)
for i in {1..100}; do
  curl -k -s https://$APP_URL/api/persistence/test -X POST \
    -H "Content-Type: application/json" \
    -d '{"data":"Load test entry '$i'"}' &
done
```

### 2. Alternative: Use Apache Bench (if available)

```bash
# High-frequency requests to trigger scaling
ab -n 1000 -c 10 https://$APP_URL/

# Or use hey (if installed)
hey -n 1000 -c 10 https://$APP_URL/
```

### 3. Monitor Scaling in Real-Time

```bash
# Terminal 1: Watch HPA status
watch -n 2 'oc get hpa demoapp3-hpa'

# Terminal 2: Watch pod scaling
watch -n 2 'oc get pods -l app=demoapp3'

# Terminal 3: Monitor resource usage
watch -n 5 'oc adm top pods -l app=demoapp3'

# Terminal 4: Check deployment scaling
watch -n 2 'oc get deployment demoapp3'
```

### 4. Observe Scaling Events

```bash
# View HPA events
oc describe hpa demoapp3-hpa

# View deployment events
oc describe deployment demoapp3

# Check cluster events
oc get events --sort-by=.metadata.creationTimestamp | tail -20
```

## 📊 Step 6: Analyze Scaling Behavior

### 1. Understanding the Scaling Metrics

```bash
# Get current metrics that HPA is using
oc get --raw /apis/metrics.k8s.io/v1beta1/namespaces/$(oc project -q)/pods | jq '.items[] | select(.metadata.labels.app=="demoapp3") | {name: .metadata.name, cpu: .containers[0].usage.cpu, memory: .containers[0].usage.memory}'
```

### 2. Resource Limit Analysis

```bash
# Compare resource requests vs limits vs actual usage
oc describe deployment demoapp3 | grep -A 10 -B 5 "Limits\|Requests"

# Check if pods are being throttled
oc adm top pods -l app=demoapp3 --sort-by=cpu
```

### 3. Scaling History

```bash
# View scaling events over time
oc get events --field-selector involvedObject.name=demoapp3-hpa --sort-by=.metadata.creationTimestamp

# Check HPA conditions
oc get hpa demoapp3-hpa -o yaml | grep -A 20 conditions:
```

## 🎯 Step 7: Advanced Scaling Operations

### 1. Manual Scaling Override

```bash
# Temporarily scale manually (HPA will adjust)
oc scale deployment demoapp3 --replicas=5

# Watch HPA respond to manual changes
oc get hpa demoapp3-hpa -w
```

### 2. Update HPA Configuration

```bash
# Lower CPU threshold to make scaling more aggressive
oc patch hpa demoapp3-hpa -p '{"spec":{"metrics":[{"type":"Resource","resource":{"name":"cpu","target":{"type":"Utilization","averageUtilization":30}}}]}}'

# Reset to original values
oc patch hpa demoapp3-hpa -p '{"spec":{"metrics":[{"type":"Resource","resource":{"name":"cpu","target":{"type":"Utilization","averageUtilization":50}}}]}}'
```

### 3. Scaling Policies Testing

```bash
# Test scale-down behavior by stopping load
# Kill load generation scripts and watch scale-down (takes ~5 minutes)

# View current scaling policies
oc get hpa demoapp3-hpa -o yaml | grep -A 20 behavior:
```

## 🔬 Step 8: Database Performance Under Load

### 1. Check Database Connection Pool

```bash
# Connect to PostgreSQL and check active connections
oc exec -it deployment/postgresql -- psql -U demo_user -d demo_db -c "SELECT count(*) as active_connections FROM pg_stat_activity WHERE state = 'active';"

# Check total connections
oc exec -it deployment/postgresql -- psql -U demo_user -d demo_db -c "SELECT count(*) as total_connections FROM pg_stat_activity;"
```

### 2. Monitor Database Performance

```bash
# Check database resource usage during scaling
oc adm top pods -l app=postgresql

# View database slow queries (if any)
oc exec -it deployment/postgresql -- psql -U demo_user -d demo_db -c "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

## ✅ Verification Checklist

You've successfully completed Step 5 when:

- ✅ Demo App V3 is deployed with resource limits
- ✅ HPA is configured and showing current metrics
- ✅ Load testing triggers automatic pod scaling (2 → more pods)
- ✅ Pods scale back down when load decreases (after ~5 minutes)
- ✅ Application shows "Step 5" as highlighted
- ✅ All scaled pods share the same database and show consistent data

## 🎓 Key Concepts Demonstrated

### Resource Management
- **CPU and Memory Limits:** Prevent resource overconsumption
- **Requests vs Limits:** Guaranteed vs maximum resource allocation
- **Resource Utilization:** How HPA makes scaling decisions

### Horizontal Pod Autoscaling
- **Metrics-Based Scaling:** CPU and memory thresholds
- **Scaling Policies:** Control how fast scaling happens
- **Stabilization Windows:** Prevent rapid scaling fluctuations

### Production Patterns
- **Load Balancing:** Traffic distributed across scaled pods
- **Shared State:** Database handles multiple application instances
- **Health Checks:** Ensure only healthy pods receive traffic

## 🔍 Troubleshooting

### HPA Not Scaling

```bash
# Check if metrics-server is available
oc get apiservices | grep metrics

# Verify resource requests are set (required for HPA)
oc describe deployment demoapp3 | grep -A 5 -B 5 "Requests"

# Check HPA conditions
oc describe hpa demoapp3-hpa
```

### Pods Not Getting Load

```bash
# Verify service endpoints
oc get endpoints demoapp3-service

# Test service connectivity
oc exec -it deployment/demoapp3 -- curl localhost:8080/api/health
```

### Resource Limits Too Low

```bash
# Check for OOMKilled or CPU throttling
oc describe pods -l app=demoapp3 | grep -A 5 -B 5 "OOMKilled\|Reason"

# Adjust limits if needed
oc patch deployment demoapp3 -p '{"spec":{"template":{"spec":{"containers":[{"name":"demoapp3","resources":{"limits":{"memory":"512Mi","cpu":"500m"}}}]}}}}'
```

## 📝 What's Next?

You've successfully implemented horizontal pod autoscaling and resource management. Your applications now automatically scale based on load, but there's still one critical production concern: health monitoring.

In **Step 6**, you'll deploy Demo App V4 which focuses on:
- 🏥 **Health Probe Configuration** (liveness, readiness, startup)
- 🔧 **Production Health Monitoring** patterns  
- 🚨 **Self-Healing Container** behaviors
- ✅ **Step 6 Completion Workflow** based on probe configuration

---

**Ready for production health monitoring?** 🚀 [Continue to Step 6: Health Probes →](step-6-demo-app-v4.md)

*Excellent work! You've mastered resource management and autoscaling - critical skills for production OpenShift deployments.* 🎉