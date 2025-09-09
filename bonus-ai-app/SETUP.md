# Bonus AI App - Quick Setup Guide

## 🚀 Quick Start (Recommended)

This is the simplified approach that avoids complex CSI driver setup and works reliably on ROKS clusters.

### Step 1: Get Anthropic API Key

1. **Sign up at Anthropic**: https://console.anthropic.com/
2. **Create API Key**: Go to API Keys → Create Key
3. **Copy the key** (starts with `sk-ant-...`)

### Step 2: Configure the Secret

Edit `openshift/anthropic-secret.yaml`:

```bash
# Base64 encode your API key
echo -n "your-actual-anthropic-api-key" | base64

# Copy the output and replace the placeholder in anthropic-secret.yaml
```

Example:
```yaml
data:
  ANTHROPIC_API_KEY: c2stYW50LWFwaTE5OTktMDMtMjBUMDA6MDA6MDBaLXNvbWV0aGluZw==
```

### Step 3: Deploy the Application

```bash
# Run the simplified deployment script
./deploy-simple.sh
```

That's it! The script will:
- Create the namespace and resources
- Build the application from source
- Deploy with health probes and persistent storage
- Provide you with the application URL

## 🎯 What You Get

### AI-Powered Cat Facts
- Uses **Claude 3 Haiku** (cheapest Anthropic model)
- Topic-based fact generation
- Real-time AI responses

### Vector Database
- **ChromaDB** for semantic search
- Persistent storage (5Gi PVC)
- Search through generated facts

### Production Features
- Health probes (startup, liveness, readiness)
- Resource limits and scaling
- Comprehensive monitoring

## 🔧 Manual Setup (Alternative)

If you prefer manual deployment:

```bash
# 1. Create namespace
oc apply -f openshift/namespace.yaml

# 2. Configure API key secret (edit first!)
oc apply -f openshift/anthropic-secret.yaml

# 3. Create storage
oc apply -f openshift/pvc.yaml

# 4. Build application
oc apply -f openshift/buildconfig.yaml
oc apply -f openshift/imagestream.yaml
oc start-build bonus-ai-app -n bonus-ai-app --follow

# 5. Deploy application
oc apply -f openshift/deployment.yaml
oc apply -f openshift/service.yaml
oc apply -f openshift/route.yaml
```

## 🧪 Testing the App

```bash
# Get the URL
APP_URL=$(oc get route bonus-ai-app -n bonus-ai-app -o jsonpath='{.spec.host}')

# Test health
curl -k "https://$APP_URL/api/health"

# Generate a cat fact
curl -k -X POST "https://$APP_URL/api/cat-fact" \
  -H "Content-Type: application/json" \
  -d '{"query": "hunting"}'

# Run demo (generates 5 facts)
curl -k "https://$APP_URL/api/demo"
```

## 🔍 Monitoring

```bash
# Check deployment status
oc get all -n bonus-ai-app

# View logs
oc logs -f deployment/bonus-ai-app -n bonus-ai-app

# Check resource usage
oc adm top pods -l app=bonus-ai-app -n bonus-ai-app

# Scale the application
oc scale deployment bonus-ai-app --replicas=3 -n bonus-ai-app
```

## 🎓 Learning Focus

This bonus app demonstrates:

1. **AI API Integration**: Real-world AI service consumption
2. **Vector Databases**: Modern semantic search patterns
3. **OpenShift Production**: Health probes, scaling, monitoring
4. **Secret Management**: Secure API key handling
5. **Persistent Storage**: Vector database data survival

## 💡 Cost Optimization

- **Anthropic Model**: Uses Claude 3 Haiku (cheapest option)
- **Resources**: Right-sized for development (512Mi RAM, 200m CPU)
- **Storage**: Minimal 5Gi for vector database
- **Single Replica**: Default scaling for cost control

## 🆘 Troubleshooting

### Build Fails
```bash
# Check build logs
oc logs -f bc/bonus-ai-app -n bonus-ai-app

# Restart build
oc start-build bonus-ai-app -n bonus-ai-app --follow
```

### App Won't Start
```bash
# Check pod events
oc describe pod -l app=bonus-ai-app -n bonus-ai-app

# Check application logs
oc logs deployment/bonus-ai-app -n bonus-ai-app

# Verify API key secret
oc get secret anthropic-api-key -n bonus-ai-app -o yaml
```

### Vector DB Issues
```bash
# Check PVC status
oc get pvc vector-db-storage -n bonus-ai-app

# Check volume mounting
oc exec -it deployment/bonus-ai-app -n bonus-ai-app -- ls -la /data
```

---

**🎉 Ready to explore AI + Vector Database on OpenShift!** 

Visit the web interface to start generating AI-powered cat facts and see the vector database in action.