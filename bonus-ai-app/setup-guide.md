# Bonus AI App Setup Guide

## Prerequisites Setup

### 1. Store Anthropic API Key in IBM Secrets Manager

1. **Get your Anthropic API Key:**
   - Visit https://console.anthropic.com/
   - Create an account and generate an API key
   - Note: This app uses Claude 3 Haiku (cheapest model)

2. **Add to IBM Secrets Manager:**
   ```bash
   # Using IBM Cloud CLI (if available)
   ibmcloud secrets-manager secret-create \
     --secret-type arbitrary \
     --name "anthropic-api-key" \
     --payload "your-actual-api-key-here"
   ```
   
   Or via the IBM Cloud console:
   - Go to your Secrets Manager instance
   - Create → Arbitrary secret
   - Name: `anthropic-api-key`
   - Secret: Your Anthropic API key
   - Note the secret ID

### 2. Get Required IBM Cloud Information

You'll need these values:
- **IBM Cloud API Key** (with Secrets Manager access)
- **Secrets Manager Instance ID** (GUID)
- **Secret ID** for your Anthropic API key
- **Region** (e.g., us-south)

## Configuration Steps

### Step 1: Configure Secrets Manager Access

Edit `secrets-manager-setup/secrets-manager-config.yaml`:

```yaml
# Replace these values:
data:
  # Base64 encode your IBM Cloud API key
  apikey: <BASE64_ENCODED_IBM_CLOUD_API_KEY>
data:
  # Your Secrets Manager instance GUID
  instance-id: "<YOUR_INSTANCE_ID>"
  region: "us-south"  # Your region
  endpoint: "https://<YOUR_INSTANCE_ID>.us-south.secrets-manager.appdomain.cloud"
```

**To base64 encode your API key:**
```bash
echo -n "your-ibm-cloud-api-key" | base64
```

### Step 2: Configure Secrets Provider

Edit `openshift/secrets-provider.yaml`:

```yaml
# Replace these values in the parameters section:
parameters:
  secretsManagerEndpoint: "https://<YOUR_INSTANCE_ID>.us-south.secrets-manager.appdomain.cloud" # pragma: allowlist secret
  secretsManagerInstanceId: "<YOUR_INSTANCE_ID>" 
  secrets: |
    - secretName: "anthropic-api-key" # pragma: allowlist secret
      secretId: "<YOUR_SECRET_ID>"  # pragma: allowlist secret
      secretType: "arbitrary" # pragma: allowlist secret
```

### Step 3: Update Authentication Secret

In `openshift/secrets-provider.yaml`, also update:

```yaml
data:
  # Base64 encoded IBM Cloud API key
  apikey: <BASE64_ENCODED_IBM_CLOUD_API_KEY> # pragma: allowlist secret
```

## Deployment

### Quick Deployment

```bash
# Make sure you're in the bonus-ai-app directory
cd bonus-ai-app

# Run the deployment script
./deploy.sh
```

### Manual Deployment

If you prefer step-by-step deployment:

```bash
# 1. Deploy CSI Driver
oc apply -f secrets-manager-setup/secrets-manager-csi-driver.yaml

# 2. Deploy namespace and config
oc apply -f openshift/namespace.yaml
oc apply -f secrets-manager-setup/secrets-manager-config.yaml

# 3. Create storage
oc apply -f openshift/pvc.yaml

# 4. Configure secrets
oc apply -f openshift/secrets-provider.yaml

# 5. Build application
oc apply -f openshift/buildconfig.yaml
oc apply -f openshift/imagestream.yaml
oc start-build bonus-ai-app -n bonus-ai-app --follow

# 6. Deploy application
oc apply -f openshift/deployment.yaml
oc apply -f openshift/service.yaml
oc apply -f openshift/route.yaml
```

## Verification

### Check Deployment Status

```bash
# Check all resources
oc get all -n bonus-ai-app

# Check secrets mounting
oc describe pod -l app=bonus-ai-app -n bonus-ai-app

# Check logs
oc logs -f deployment/bonus-ai-app -n bonus-ai-app
```

### Test the Application

```bash
# Get application URL
APP_URL=$(oc get route bonus-ai-app -n bonus-ai-app -o jsonpath='{.spec.host}')

# Test health endpoint
curl -k "https://$APP_URL/api/health"

# Generate a cat fact
curl -k -X POST "https://$APP_URL/api/cat-fact" \
  -H "Content-Type: application/json" \
  -d '{"query": "hunting"}'
```

## Troubleshooting

### Secrets Not Loading

```bash
# Check CSI driver status
oc get pods -n secrets-manager-csi-driver

# Check secret provider class
oc describe secretproviderclass anthropic-secrets -n bonus-ai-app

# Check if secret was created
oc get secrets anthropic-api-key -n bonus-ai-app
```

### Build Issues

```bash
# Check build logs
oc logs -f bc/bonus-ai-app -n bonus-ai-app

# Rebuild if needed
oc start-build bonus-ai-app -n bonus-ai-app --follow
```

### Application Not Starting

```bash
# Check pod events
oc describe pod -l app=bonus-ai-app -n bonus-ai-app

# Check application logs
oc logs deployment/bonus-ai-app -n bonus-ai-app

# Check resource availability
oc describe node | grep -A 5 "Allocated resources"
```

### Vector Database Issues

```bash
# Check PVC status
oc get pvc vector-db-storage -n bonus-ai-app

# Check volume mounting
oc exec -it deployment/bonus-ai-app -n bonus-ai-app -- ls -la /data

# Check permissions
oc exec -it deployment/bonus-ai-app -n bonus-ai-app -- id
```

## Cost Optimization Notes

- **Anthropic Model**: Uses Claude 3 Haiku (cheapest model)
- **Resources**: Configured for development use (512Mi memory, 200m CPU)
- **Storage**: 5Gi PVC for vector database
- **Scaling**: Single replica by default

For production, consider:
- Increasing resource limits
- Adding horizontal pod autoscaling  
- Implementing caching layers
- Using read replicas for the vector database
