#!/bin/bash

# Auto-deploy script for demo-app-v3
# Usage: ./deploy.sh [--build] [--follow]

set -e

PROJECT="demo-app-v3"
NAMESPACE="demo-lab-apps"

echo "🚀 Starting deployment for $PROJECT..."

# Check if we should trigger a new build
if [[ "$1" == "--build" || "$1" == "-b" ]]; then
    echo "📦 Starting new build..."
    oc start-build $PROJECT
    
    if [[ "$2" == "--follow" || "$2" == "-f" ]]; then
        echo "👀 Following build logs..."
        oc logs -f buildconfig/$PROJECT
    else
        # Wait for build to complete
        echo "⏳ Waiting for build to complete..."
        oc wait --for=condition=Complete build -l buildconfig=$PROJECT --timeout=300s
    fi
fi

# Get the latest image hash to force a rollout
LATEST_IMAGE=$(oc get imagestream $PROJECT -o jsonpath='{.status.tags[?(@.tag=="latest")].items[0].dockerImageReference}')

if [[ -n "$LATEST_IMAGE" ]]; then
    echo "📋 Latest image: $LATEST_IMAGE"
    
    # Update deployment with latest image
    oc patch deployment $PROJECT -p "{\"spec\":{\"template\":{\"spec\":{\"containers\":[{\"name\":\"$PROJECT\",\"image\":\"$LATEST_IMAGE\"}]}}}}"
    
    # Trigger rollout
    echo "🔄 Rolling out new deployment..."
    oc rollout restart deployment/$PROJECT
    
    # Monitor rollout
    echo "📊 Monitoring rollout status..."
    oc rollout status deployment/$PROJECT --timeout=300s
    
    echo "✅ Deployment completed successfully!"
    
    # Show running pods
    echo "📱 Current pods:"
    oc get pods -l app=$PROJECT
else
    echo "❌ Could not find latest image. Build may have failed."
    exit 1
fi