#!/bin/bash

# Simplified Bonus AI App Deployment Script
# This script deploys the AI Cat Facts application without CSI driver complexity

set -e

echo "🤖 Starting Simplified Bonus AI App Deployment"
echo "=============================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if oc is available
if ! command -v oc &> /dev/null; then
    print_error "OpenShift CLI (oc) is not installed or not in PATH"
    exit 1
fi

# Check if logged into OpenShift
if ! oc whoami &> /dev/null; then
    print_error "Not logged into OpenShift. Please run 'oc login' first."
    exit 1
fi

print_success "OpenShift CLI ready"

# Step 1: Create namespace
print_status "Step 1: Creating namespace..."
oc apply -f openshift/namespace.yaml
print_success "Namespace created"

# Step 2: Check Anthropic API key secret
print_status "Step 2: Configuring Anthropic API key..."

if grep -q "REPLACE_WITH" openshift/anthropic-secret.yaml; then
    print_warning "⚠️  Anthropic API key secret contains placeholder values!"
    print_warning "Please update openshift/anthropic-secret.yaml with:"
    print_warning "  1. Get your Anthropic API key from https://console.anthropic.com/"
    print_warning "  2. Base64 encode it: echo -n 'your-api-key' | base64"
    print_warning "  3. Replace the placeholder in openshift/anthropic-secret.yaml"
    echo
    read -p "Have you updated the Anthropic API key? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Please update the API key and run the script again."
        exit 1
    fi
fi

oc apply -f openshift/anthropic-secret.yaml
print_success "Anthropic API key secret created"

# Step 3: Create storage
print_status "Step 3: Creating persistent storage..."
oc apply -f openshift/pvc.yaml
print_success "PVC created"

# Check PVC status
print_status "Checking PVC status..."
PVC_STATUS=$(oc get pvc vector-db-storage -n bonus-ai-app -o jsonpath='{.status.phase}' 2>/dev/null || echo "NotFound")

if [ "$PVC_STATUS" = "Bound" ]; then
    print_success "PVC is already bound"
    # Show PVC details
    PVC_SIZE=$(oc get pvc vector-db-storage -n bonus-ai-app -o jsonpath='{.status.capacity.storage}')
    PVC_STORAGE_CLASS=$(oc get pvc vector-db-storage -n bonus-ai-app -o jsonpath='{.spec.storageClassName}')
    print_status "PVC Details: ${PVC_SIZE} on ${PVC_STORAGE_CLASS}"
elif [ "$PVC_STATUS" = "Pending" ]; then
    print_status "PVC is pending, waiting for it to be bound..."
    oc wait --for=condition=bound pvc/vector-db-storage -n bonus-ai-app --timeout=300s
    print_success "PVC is now bound"
else
    print_status "PVC status: $PVC_STATUS - waiting for binding..."
    sleep 10
    oc wait --for=condition=bound pvc/vector-db-storage -n bonus-ai-app --timeout=300s || {
        print_warning "PVC binding may have timed out, checking status..."
        FINAL_STATUS=$(oc get pvc vector-db-storage -n bonus-ai-app -o jsonpath='{.status.phase}' 2>/dev/null || echo "NotFound")
        if [ "$FINAL_STATUS" = "Bound" ]; then
            print_success "PVC is bound (wait command timed out but PVC is actually ready)"
        else
            print_error "PVC failed to bind. Status: $FINAL_STATUS"
            oc describe pvc vector-db-storage -n bonus-ai-app
            exit 1
        fi
    }
    print_success "PVC is bound"
fi

# Step 4: Create Service Account
print_status "Step 4: Creating service account..."
oc apply -f secrets-manager-setup/secrets-manager-config.yaml
print_success "Service account and RBAC created"

# Step 5: Build the application
print_status "Step 5: Building application..."

oc apply -f openshift/buildconfig.yaml
oc apply -f openshift/imagestream.yaml
print_success "Build configuration created"

print_status "Starting build..."
oc start-build bonus-ai-app -n bonus-ai-app --follow

# Check if build succeeded
BUILD_STATUS=$(oc get builds -n bonus-ai-app --no-headers | tail -1 | awk '{print $4}')
if [[ "$BUILD_STATUS" == "Complete" ]]; then
    print_success "Build completed successfully"
else
    print_error "Build failed with status: $BUILD_STATUS"
    print_error "Check build logs: oc logs -f bc/bonus-ai-app -n bonus-ai-app"
    exit 1
fi

# Step 6: Deploy the application
print_status "Step 6: Deploying application..."

oc apply -f openshift/deployment.yaml
oc apply -f openshift/service.yaml
oc apply -f openshift/route.yaml
print_success "Application deployed"

# Step 7: Wait for deployment to be ready
print_status "Step 7: Waiting for application to be ready..."

oc rollout status deployment/bonus-ai-app -n bonus-ai-app --timeout=600s
print_success "Application is ready"

# Step 8: Get application URL and test
print_status "Step 8: Testing deployment..."

APP_URL=$(oc get route bonus-ai-app -n bonus-ai-app -o jsonpath='{.spec.host}')
print_success "Application URL: https://$APP_URL"

# Test health endpoint with retry
print_status "Testing health endpoint..."
for i in {1..10}; do
    if curl -k -s -f "https://$APP_URL/api/health" > /dev/null 2>&1; then
        print_success "Health check passed"
        break
    else
        if [ $i -eq 10 ]; then
            print_warning "Health check failed after 10 attempts - application may still be starting"
            print_warning "Check logs: oc logs -f deployment/bonus-ai-app -n bonus-ai-app"
        else
            print_status "Health check attempt $i failed, retrying in 10 seconds..."
            sleep 10
        fi
    fi
done

# Final status
echo
echo "🎉 Simplified Bonus AI App Deployment Complete!"
echo "==============================================="
echo
echo "Application URL: https://$APP_URL"
echo
echo "Available endpoints:"
echo "  • Web UI:     https://$APP_URL"
echo "  • Health:     https://$APP_URL/api/health"
echo "  • Cat Facts:  https://$APP_URL/api/cat-fact"
echo "  • Search:     https://$APP_URL/api/search"
echo "  • Stats:      https://$APP_URL/api/stats"
echo "  • Demo:       https://$APP_URL/api/demo"
echo
echo "To monitor the application:"
echo "  oc logs -f deployment/bonus-ai-app -n bonus-ai-app"
echo "  oc get pods -l app=bonus-ai-app -n bonus-ai-app"
echo
echo "To scale the application:"
echo "  oc scale deployment bonus-ai-app --replicas=3 -n bonus-ai-app"
echo
echo "Next steps:"
echo "  1. Visit the web UI to generate AI-powered cat facts"
echo "  2. Try the search functionality to find similar facts"
echo "  3. Run the demo to see the vector database in action"
echo

print_success "Deployment script completed successfully!"