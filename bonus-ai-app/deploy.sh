#!/bin/bash

# Bonus AI App Deployment Script
# This script deploys the AI Cat Facts application with Secrets Manager integration

set -e

echo "🤖 Starting Bonus AI App Deployment"
echo "=================================="

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

# Step 1: Create namespace and base resources
print_status "Step 1: Creating namespace and base resources..."

oc apply -f openshift/namespace.yaml
print_success "Namespace created"

# Check if anthropic-secret.yaml has been customized
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
oc apply -f secrets-manager-setup/secrets-manager-config.yaml
print_success "API key secret and service account created"

# Step 3: Deploy storage
print_status "Step 3: Creating persistent storage..."
oc apply -f openshift/pvc.yaml
print_success "PVC created"

# Check PVC status
print_status "Checking PVC status..."
PVC_STATUS=$(oc get pvc vector-db-storage -n bonus-ai-app -o jsonpath='{.status.phase}' 2>/dev/null || echo "NotFound")

if [ "$PVC_STATUS" = "Bound" ]; then
    print_success "PVC is already bound"
elif [ "$PVC_STATUS" = "Pending" ]; then
    print_status "PVC is pending, waiting for it to be bound..."
    oc wait --for=condition=bound pvc/vector-db-storage -n bonus-ai-app --timeout=300s
    print_success "PVC is now bound"
else
    print_status "PVC not found or in unknown state, waiting for binding..."
    sleep 10
    oc wait --for=condition=bound pvc/vector-db-storage -n bonus-ai-app --timeout=300s
    print_success "PVC is bound"
fi

# Step 4: Build the application
print_status "Step 4: Building application..."

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
    exit 1
fi

# Step 5: Deploy the application
print_status "Step 5: Deploying application..."

oc apply -f openshift/deployment.yaml
oc apply -f openshift/service.yaml
oc apply -f openshift/route.yaml
print_success "Application deployed"

# Step 6: Wait for deployment to be ready
print_status "Step 6: Waiting for application to be ready..."

oc rollout status deployment/bonus-ai-app -n bonus-ai-app --timeout=600s
print_success "Application is ready"

# Step 7: Get application URL and test
print_status "Step 7: Testing deployment..."

APP_URL=$(oc get route bonus-ai-app -n bonus-ai-app -o jsonpath='{.spec.host}')
print_success "Application URL: https://$APP_URL"

# Test health endpoint
print_status "Testing health endpoint..."
if curl -k -s -f "https://$APP_URL/api/health" > /dev/null; then
    print_success "Health check passed"
else
    print_warning "Health check failed - application may still be starting"
fi

# Final status
echo
echo "🎉 Bonus AI App Deployment Complete!"
echo "====================================="
echo
echo "Application URL: https://$APP_URL"
echo
echo "Available endpoints:"
echo "  • Web UI:     https://$APP_URL"
echo "  • Health:     https://$APP_URL/api/health"
echo "  • Cat Facts:  https://$APP_URL/api/cat-fact"
echo "  • Search:     https://$APP_URL/api/search"
echo "  • Stats:      https://$APP_URL/api/stats"
echo
echo "To monitor the application:"
echo "  oc logs -f deployment/bonus-ai-app -n bonus-ai-app"
echo "  oc get pods -l app=bonus-ai-app -n bonus-ai-app"
echo
echo "To scale the application:"
echo "  oc scale deployment bonus-ai-app --replicas=3 -n bonus-ai-app"
echo

print_success "Deployment script completed successfully!"