#!/bin/bash

# OpenShift Deployment Script for MkDocs Documentation Site
# This script deploys the MkDocs site with custom domain support

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE} MkDocs Documentation Site Deployment${NC}"
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

# Deploy MkDocs site
echo -e "\n${YELLOW}1. Deploying MkDocs Documentation Site...${NC}"
oc apply -f mkdocs-site.yaml

# Start build
echo -e "${YELLOW}   Starting documentation build...${NC}"
oc start-build mkdocs-site --wait

echo -e "${GREEN}✓ MkDocs site build completed${NC}"

# Wait for deployment to be ready
echo -e "\n${YELLOW}2. Waiting for deployment to be ready...${NC}"
oc rollout status deployment/mkdocs-site --timeout=300s

echo -e "${GREEN}✓ MkDocs site deployed and ready${NC}"

# Get application URL
echo -e "\n${YELLOW}3. Getting application URL...${NC}"
DOCS_URL=$(oc get route mkdocs-site-route -o jsonpath='{.spec.host}')

if [ -n "$DOCS_URL" ]; then
    echo -e "${GREEN}✓ Documentation site is available at: https://${DOCS_URL}${NC}"
    echo -e "${BLUE}Direct link: https://${DOCS_URL}${NC}"
else
    echo -e "${RED}Warning: Could not retrieve documentation URL${NC}"
fi

# Show deployment status
echo -e "\n${YELLOW}4. Deployment Status:${NC}"
echo -e "${BLUE}Documentation Site:${NC}"
oc get pods -l app=mkdocs-site

echo -e "\n${BLUE}Deployment Status:${NC}"
oc get deployment mkdocs-site

echo -e "\n${BLUE}Service:${NC}"
oc get svc mkdocs-site-service -o wide

echo -e "\n${BLUE}Route:${NC}"
oc get route mkdocs-site-route

echo -e "\n${BLUE}Build Status:${NC}"
oc get builds -l buildconfig=mkdocs-site --sort-by=.metadata.creationTimestamp

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN} Documentation Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"

if [ -n "$DOCS_URL" ]; then
    echo -e "${YELLOW}Next steps:${NC}"
    echo -e "1. Visit: ${BLUE}https://${DOCS_URL}${NC}"
    echo -e "2. Verify all documentation sections load correctly"
    echo -e "3. Test navigation and search functionality"
    echo -e "4. Share the documentation URL with lab participants"
    echo -e "\n${BLUE}Documentation Features:${NC}"
    echo -e "• Comprehensive lab guides and tutorials"
    echo -e "• Interactive architecture diagrams"
    echo -e "• Step-by-step OpenShift deployment instructions"
    echo -e "• Search functionality across all content"
    echo -e "• Mobile-responsive design"
    echo -e "• Dark/light theme toggle"
fi