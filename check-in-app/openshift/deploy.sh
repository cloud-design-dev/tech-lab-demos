#!/bin/bash

# OpenShift Deployment Script for Check-in App
# This script deploys the check-in application with PostgreSQL backend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE} OpenShift Check-in App Deployment${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if oc is available
if ! command -v oc &> /dev/null; then
    echo -e "${RED}Error: OpenShift CLI (oc) is not installed or not in PATH${NC}"
    exit 1
fi

# Check if logged in to OpenShift
if ! oc whoami &> /dev/null; then
    echo -e "${RED}Error: Not logged in to OpenShift. Please run 'oc login' first${NC}"
    exit 1
fi

echo -e "${GREEN}✓ OpenShift CLI available and logged in${NC}"

# Get current project
PROJECT=$(oc project -q)
echo -e "${BLUE}Deploying to project: ${PROJECT}${NC}"

# Deploy PostgreSQL first
echo -e "\n${YELLOW}1. Deploying PostgreSQL with 20GB PVC...${NC}"
oc apply -f postgresql.yaml

# Wait for PostgreSQL to be ready
echo -e "${YELLOW}   Waiting for PostgreSQL to be ready...${NC}"
oc wait --for=condition=available --timeout=300s deployment/postgresql

echo -e "${GREEN}✓ PostgreSQL deployed and ready${NC}"

# Deploy Check-in App
echo -e "\n${YELLOW}2. Deploying Check-in Application...${NC}"

# Check if secrets need to be updated
echo -e "${YELLOW}   Checking IBM Cloud credentials...${NC}"
if [ -z "$IBM_CLOUD_API_KEY" ] || [ -z "$IBM_CLOUD_ACCOUNT_ID" ]; then
    echo -e "${RED}Warning: IBM_CLOUD_API_KEY and/or IBM_CLOUD_ACCOUNT_ID environment variables not set${NC}"
    echo -e "${YELLOW}The app will use fallback authentication. Set these variables for production use:${NC}"
    echo -e "${YELLOW}  export IBM_CLOUD_API_KEY=your-api-key${NC}"
    echo -e "${YELLOW}  export IBM_CLOUD_ACCOUNT_ID=your-account-id${NC}"
else
    # Update secrets with provided credentials
    echo -e "${GREEN}✓ IBM Cloud credentials found, updating secret...${NC}"
    
    # Create temporary secret patch
    cat > secret-patch.yaml << EOF
data:
  IBM_CLOUD_API_KEY: $(echo -n "$IBM_CLOUD_API_KEY" | base64 | tr -d '\n')
  IBM_CLOUD_ACCOUNT_ID: $(echo -n "$IBM_CLOUD_ACCOUNT_ID" | base64 | tr -d '\n')
EOF
    
    # Apply the main manifest first
    oc apply -f checkin-app.yaml
    
    # Patch the secret with actual credentials
    oc patch secret checkin-app-secret --patch-file secret-patch.yaml
    
    # Clean up temp file
    rm secret-patch.yaml
fi

# If credentials weren't provided via env vars, just apply the manifest
if [ -z "$IBM_CLOUD_API_KEY" ] || [ -z "$IBM_CLOUD_ACCOUNT_ID" ]; then
    oc apply -f checkin-app.yaml
fi

# Start build if BuildConfig exists
echo -e "${YELLOW}   Starting application build...${NC}"
oc start-build checkin-app --wait

# Wait for deployment to be ready (using standard Deployment instead of DeploymentConfig)
echo -e "${YELLOW}   Waiting for Check-in app to be ready...${NC}"
oc rollout status deployment/checkin-app --timeout=300s

echo -e "${GREEN}✓ Check-in application deployed and ready${NC}"

# Get application URL
echo -e "\n${YELLOW}3. Getting application URL...${NC}"
APP_URL=$(oc get route checkin-app-route -o jsonpath='{.spec.host}')

if [ -n "$APP_URL" ]; then
    echo -e "${GREEN}✓ Application is available at: https://${APP_URL}${NC}"
    echo -e "${BLUE}Admin login: https://${APP_URL}/admin/login${NC}"
    echo -e "${BLUE}Admin password: demo-admin-2024 (change in production)${NC}"
else
    echo -e "${RED}Warning: Could not retrieve application URL${NC}"
fi

# Show deployment status
echo -e "\n${YELLOW}4. Deployment Status:${NC}"
echo -e "${BLUE}PostgreSQL:${NC}"
oc get pods -l app=postgresql
echo -e "\n${BLUE}Check-in App:${NC}"
oc get pods -l app=checkin-app
echo -e "\n${BLUE}Deployment Status:${NC}"
oc get deployment checkin-app
echo -e "\n${BLUE}Services:${NC}"
oc get svc -l app=postgresql -o wide
oc get svc -l app=checkin-app -o wide
echo -e "\n${BLUE}Storage:${NC}"
oc get pvc postgresql-pvc
echo -e "\n${BLUE}Build Status:${NC}"
oc get builds -l buildconfig=checkin-app --sort-by=.metadata.creationTimestamp

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN} Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"

# Get GitHub webhook URL for setup
WEBHOOK_URL=$(oc describe bc/checkin-app | grep "Webhook GitHub:" | awk '{print $3}')

if [ -n "$APP_URL" ]; then
    echo -e "${YELLOW}Next steps:${NC}"
    echo -e "1. Visit: ${BLUE}https://${APP_URL}${NC}"
    echo -e "2. Admin access: ${BLUE}https://${APP_URL}/admin/login${NC}"
    echo -e "3. Update IBM Cloud credentials in secret if needed"
    echo -e "4. Change admin password in production"
    
    if [ -n "$WEBHOOK_URL" ]; then
        echo -e "5. Set up GitHub webhook for automated builds:"
        echo -e "   ${BLUE}Webhook URL: ${WEBHOOK_URL}${NC}"
        echo -e "   ${BLUE}Content Type: application/json${NC}"
        echo -e "   ${BLUE}Secret: webhook-secret-2024${NC}"
        echo -e "   ${BLUE}Events: Just push events${NC}"
    fi
fi