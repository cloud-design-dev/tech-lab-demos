#!/bin/bash

# IBM Cloud Code Engine Deployment Script for Check-in App
# This script deploys the check-in application to IBM Cloud Code Engine

set -e

# Configuration
PROJECT_NAME="checkin-app"
APP_NAME="checkin-app"
IMAGE_NAME="icr.io/${ICR_NAMESPACE}/checkin-app:latest"
POSTGRES_INSTANCE_NAME="checkin-postgres"
SERVICE_KEY_NAME="checkin-postgres-key" # pragma: allowlist secret

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check required environment variables
check_env_vars() {
    echo_info "Checking required environment variables..."
    
    required_vars=("ICR_NAMESPACE" "IBM_CLOUD_API_KEY" "IBM_CLOUD_ACCOUNT_ID" "FLASK_SECRET_KEY" "ADMIN_PASSWORD")
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            echo_error "Environment variable $var is not set"
            exit 1
        fi
    done
    
    echo_info "All required environment variables are set"
}

# Build and push Docker image
build_and_push_image() {
    echo_info "Building and pushing Docker image..."
    
    # Build image
    docker build -t $IMAGE_NAME .
    
    # Push to IBM Cloud Container Registry
    docker push $IMAGE_NAME
    
    echo_info "Image built and pushed successfully"
}

# Create or select Code Engine project
setup_project() {
    echo_info "Setting up Code Engine project..."
    
    # Check if project exists
    if ibmcloud ce project get --name $PROJECT_NAME >/dev/null 2>&1; then
        echo_info "Project $PROJECT_NAME already exists, selecting it"
        ibmcloud ce project select --name $PROJECT_NAME
    else
        echo_info "Creating new project $PROJECT_NAME"
        ibmcloud ce project create --name $PROJECT_NAME
    fi
}

# Get PostgreSQL connection string
get_postgres_connection() {
    echo_info "Getting PostgreSQL connection information..."
    
    # Check if service key exists
    if ! ibmcloud resource service-key $SERVICE_KEY_NAME >/dev/null 2>&1; then
        echo_warn "Service key $SERVICE_KEY_NAME not found, creating it..."
        ibmcloud resource service-key-create $SERVICE_KEY_NAME Manager --instance-name $POSTGRES_INSTANCE_NAME
    fi
    
    # Get connection string
    CONNECTION_JSON=$(ibmcloud resource service-key $SERVICE_KEY_NAME --output json | jq -r '.[0].credentials')
    
    if [[ "$CONNECTION_JSON" == "null" || -z "$CONNECTION_JSON" ]]; then
        echo_error "Failed to get PostgreSQL connection information"
        exit 1
    fi
    
    echo_info "PostgreSQL connection information retrieved"
}

# Deploy application to Code Engine
deploy_application() {
    echo_info "Deploying application to Code Engine..."
    
    # Check if application exists
    if ibmcloud ce application get --name $APP_NAME >/dev/null 2>&1; then
        echo_info "Application $APP_NAME exists, updating it"
        ibmcloud ce application update --name $APP_NAME \
            --image $IMAGE_NAME \
            --port 8080 \
            --min-scale 1 \
            --max-scale 10 \
            --cpu 0.25 \
            --memory 0.5G \
            --env DATABASES_FOR_POSTGRESQL_CONNECTION="$CONNECTION_JSON" \
            --env IBM_CLOUD_API_KEY="$IBM_CLOUD_API_KEY" \
            --env IBM_CLOUD_ACCOUNT_ID="$IBM_CLOUD_ACCOUNT_ID" \
            --env FLASK_SECRET_KEY="$FLASK_SECRET_KEY" \
            --env ADMIN_PASSWORD="$ADMIN_PASSWORD" \
            --env PORT=8080
    else
        echo_info "Creating new application $APP_NAME"
        ibmcloud ce application create --name $APP_NAME \
            --image $IMAGE_NAME \
            --port 8080 \
            --min-scale 1 \
            --max-scale 10 \
            --cpu 0.25 \
            --memory 0.5G \
            --env DATABASES_FOR_POSTGRESQL_CONNECTION="$CONNECTION_JSON" \
            --env IBM_CLOUD_API_KEY="$IBM_CLOUD_API_KEY" \
            --env IBM_CLOUD_ACCOUNT_ID="$IBM_CLOUD_ACCOUNT_ID" \
            --env FLASK_SECRET_KEY="$FLASK_SECRET_KEY" \
            --env ADMIN_PASSWORD="$ADMIN_PASSWORD" \
            --env PORT=8080
    fi
    
    echo_info "Application deployed successfully"
}

# Get application URL
get_app_url() {
    echo_info "Getting application URL..."
    
    APP_URL=$(ibmcloud ce application get --name $APP_NAME --output json | jq -r '.status.url')
    
    if [[ "$APP_URL" != "null" && -n "$APP_URL" ]]; then
        echo_info "Application is available at: $APP_URL"
        echo_info "Admin dashboard: $APP_URL/registered"
        echo_info "Health check: $APP_URL/api/health"
    else
        echo_warn "Could not retrieve application URL"
    fi
}

# Main deployment flow
main() {
    echo_info "Starting IBM Cloud Code Engine deployment for Check-in App"
    
    check_env_vars
    build_and_push_image
    setup_project
    get_postgres_connection
    deploy_application
    get_app_url
    
    echo_info "Deployment completed successfully!"
}

# Run main function
main "$@"
