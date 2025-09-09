# Bonus AI App - Cat Facts with Anthropic Claude & Vector Database

This is a bonus lab application that demonstrates advanced AI integration with OpenShift, featuring:

- **Anthropic Claude API** for AI-powered cat fact generation
- **ChromaDB Vector Database** for semantic search and storage
- **IBM Secrets Manager** integration for secure API key management
- **Production-ready deployment** on OpenShift with health probes

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  OpenShift      │    │ IBM Secrets      │    │ Anthropic API   │
│  Container      │◄──►│ Manager          │    │ (Claude)        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌──────────────────┐
│ ChromaDB        │    │ Persistent       │
│ Vector Database │◄──►│ Storage (PVC)    │
└─────────────────┘    └──────────────────┘
```

## 🚀 Features

### AI-Powered Cat Facts
- Uses **Claude 3 Haiku** (cheapest Anthropic model) for cost-effective generation
- Topic-based fact generation (behavior, hunting, sleeping, etc.)
- Real-time AI responses with proper error handling

### Vector Database Storage
- **ChromaDB** for semantic similarity search
- Persistent storage with OpenShift PVC
- Advanced search capabilities across stored facts

### Enterprise Security
- **IBM Secrets Manager** integration via CSI driver
- Secure API key management
- Zero secrets in container images or code

### Production Ready
- Health probes (startup, liveness, readiness)
- Resource limits and requests
- Horizontal scaling capability
- Comprehensive monitoring

## 📋 Prerequisites

Before deploying this bonus app:

1. **Anthropic API Key** stored in IBM Secrets Manager
2. **IBM Cloud API Key** with Secrets Manager access
3. **OpenShift cluster** with appropriate storage classes
4. **Completed main lab steps** (1-6) for PostgreSQL and basic concepts

## 🔧 Setup Instructions

### Step 1: Configure IBM Secrets Manager

1. **Store Anthropic API Key in Secrets Manager:**
   ```bash
   # Add your Anthropic API key to IBM Secrets Manager
   # Note the secret ID for later configuration
   ```

2. **Update Secrets Manager Configuration:**
   ```bash
   # Edit secrets-manager-setup/secrets-manager-config.yaml
   # Replace placeholders with your actual values:
   # - instance-id: Your Secrets Manager instance GUID
   # - region: Your IBM Cloud region
   # - Base64 encode your IBM Cloud API key
   ```

### Step 2: Deploy Secrets Manager CSI Driver

```bash
# Deploy the CSI driver for Secrets Manager integration
oc apply -f secrets-manager-setup/secrets-manager-csi-driver.yaml

# Deploy configuration
oc apply -f secrets-manager-setup/secrets-manager-config.yaml
```

### Step 3: Deploy the Application

```bash
# Create namespace and base resources
oc apply -f openshift/namespace.yaml
oc apply -f openshift/pvc.yaml

# Configure secrets provider (update with your values first)
oc apply -f openshift/secrets-provider.yaml

# Deploy application components
oc apply -f openshift/buildconfig.yaml
oc apply -f openshift/imagestream.yaml

# Start the build
oc start-build bonus-ai-app --follow

# Deploy the application
oc apply -f openshift/deployment.yaml
oc apply -f openshift/service.yaml
oc apply -f openshift/route.yaml
```

### Step 4: Verify Deployment

```bash
# Check all components
oc get all -n bonus-ai-app

# Check secrets integration
oc describe pod -l app=bonus-ai-app -n bonus-ai-app

# Get application URL
oc get route bonus-ai-app -n bonus-ai-app -o jsonpath='{.spec.host}'

# Test the application
curl -k https://$(oc get route bonus-ai-app -n bonus-ai-app -o jsonpath='{.spec.host}')/api/health
```

## 🎯 Usage Guide

### Web Interface
1. Access the application URL in your browser
2. **Generate Facts**: Use the AI to create new cat facts
3. **Search Database**: Find similar facts using vector search
4. **View Stats**: Monitor database and AI usage

### API Endpoints

```bash
# Health check
GET /api/health

# Generate cat fact
POST /api/cat-fact
{
  "query": "hunting behavior"  # optional topic
}

# Search similar facts
POST /api/search
{
  "query": "sleeping",
  "limit": 5
}

# Get all facts
GET /api/facts?limit=20

# Database statistics
GET /api/stats

# Run demo (generates 5 facts)
GET /api/demo
```

## 🔍 Key Technologies

### Anthropic Claude API
- **Model**: claude-3-haiku-20240307 (cost-optimized)
- **Purpose**: Intelligent cat fact generation
- **Features**: Topic-based responses, natural language processing

### ChromaDB Vector Database
- **Type**: Open-source vector database
- **Features**: Semantic similarity search, embeddings
- **Storage**: Persistent via OpenShift PVC

### IBM Secrets Manager Integration
- **Security**: External secret management
- **Method**: CSI driver with SecretProviderClass
- **Benefits**: No secrets in container images

## 📊 Monitoring & Operations

### Health Checks
- **Startup Probe**: 30s initial delay, checks AI service initialization
- **Liveness Probe**: 60s interval, monitors application health  
- **Readiness Probe**: 30s interval, controls traffic routing

### Scaling
```bash
# Scale the application
oc scale deployment bonus-ai-app --replicas=3 -n bonus-ai-app

# Monitor scaling
oc get pods -l app=bonus-ai-app -n bonus-ai-app -w
```

### Logs & Debugging
```bash
# View application logs
oc logs -f deployment/bonus-ai-app -n bonus-ai-app

# Check secrets mounting
oc exec -it deployment/bonus-ai-app -n bonus-ai-app -- ls -la /mnt/secrets

# Debug vector database
oc exec -it deployment/bonus-ai-app -n bonus-ai-app -- ls -la /data
```

## 🎓 Learning Outcomes

This bonus app demonstrates:

1. **AI Integration**: Real-world API integration with cost optimization
2. **Vector Databases**: Modern semantic search and storage patterns  
3. **Enterprise Security**: External secret management best practices
4. **Advanced OpenShift**: CSI drivers, custom resources, complex deployments
5. **Production Patterns**: Comprehensive health monitoring and scaling

## 🔍 Troubleshooting

### Common Issues

**Anthropic API Key Not Found:**
```bash
# Check secret mounting
oc describe pod -l app=bonus-ai-app -n bonus-ai-app | grep -A 10 "Mounts:"

# Verify Secrets Manager integration
oc logs -n secrets-manager-csi-driver -l app=secrets-manager-csi-driver
```

**Vector Database Initialization Failed:**
```bash
# Check PVC status
oc get pvc vector-db-storage -n bonus-ai-app

# Check storage permissions
oc exec -it deployment/bonus-ai-app -n bonus-ai-app -- ls -la /data
```

**Build Failures:**
```bash
# Check build logs
oc logs -f bc/bonus-ai-app -n bonus-ai-app

# Rebuild if needed
oc start-build bonus-ai-app -n bonus-ai-app --follow
```

## 🌟 Bonus Challenges

1. **Add More AI Models**: Integrate additional Anthropic models
2. **Enhanced Search**: Implement advanced vector search features
3. **User Authentication**: Add IBM AppID integration
4. **Metrics & Monitoring**: Add Prometheus metrics
5. **Multi-Language**: Support facts in different languages

---

**🎉 Congratulations!** You've deployed an enterprise-grade AI application with vector database storage and secure secret management on OpenShift!