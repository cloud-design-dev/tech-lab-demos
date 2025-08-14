# GitHub Webhook Setup Guide

This guide explains how to set up GitHub webhooks for automated builds when code is pushed to the repository.

## Overview

The check-in app uses OpenShift BuildConfig with GitHub webhook integration to automatically trigger new builds when code changes are pushed to the main branch.

## Setup Steps

### 1. Deploy the Application

First, deploy the application using the standard deployment process:

```bash
./deploy.sh
```

### 2. Get the Webhook URL

After deployment, get the webhook URL from the BuildConfig:

```bash
oc describe bc/checkin-app | grep "Webhook GitHub:"
```

Or use this one-liner:
```bash
WEBHOOK_URL=$(oc describe bc/checkin-app | grep "Webhook GitHub:" | awk '{print $3}')
echo "Webhook URL: $WEBHOOK_URL"
```

### 3. Configure GitHub Webhook

1. Go to your GitHub repository: https://github.com/cloud-design-dev/tech-lab-demos
2. Navigate to **Settings** → **Webhooks** → **Add webhook**
3. Configure the webhook:
   - **Payload URL**: Use the webhook URL from step 2
   - **Content type**: `application/json`
   - **Secret**: `webhook-secret-2024` (or your custom secret)
   - **Which events would you like to trigger this webhook?**: Just the push event
   - **Active**: ✅ (checked)
4. Click **Add webhook**

### 4. Test the Webhook

Test the webhook by making a commit to the main branch:

```bash
# Make a small change and push
git add .
git commit -m "Test webhook trigger"
git push origin main
```

### 5. Monitor the Build

Watch the build process in OpenShift:

```bash
# Watch builds
oc get builds -w

# Follow build logs
oc logs -f bc/checkin-app

# Check build status
oc get builds -l buildconfig=checkin-app --sort-by=.metadata.creationTimestamp
```

## Webhook Configuration Details

### Default Webhook Secret

The default webhook secret is `webhook-secret-2024`. To change this:

1. Update the secret in the manifest:
   ```bash
   echo -n "your-new-secret" | base64
   # Use the output to update the WebHookSecretKey in checkin-app.yaml
   ```

2. Update the secret in OpenShift:
   ```bash
   oc patch secret github-webhook-secret -p '{"data":{"WebHookSecretKey":"'"$(echo -n 'your-new-secret' | base64)"'"}}'
   ```

3. Update the GitHub webhook configuration with the new secret

### Webhook URL Format

The webhook URL follows this pattern:
```
https://api.<cluster-domain>/apis/build.openshift.io/v1/namespaces/<namespace>/buildconfigs/<buildconfig-name>/webhooks/<secret>/github
```

## Troubleshooting

### Webhook Not Triggering

1. **Check webhook delivery**: In GitHub, go to the webhook settings and check the "Recent Deliveries" tab
2. **Verify secret**: Ensure the secret matches between GitHub and OpenShift
3. **Check BuildConfig**: Verify the BuildConfig has the GitHub trigger:
   ```bash
   oc get bc/checkin-app -o yaml | grep -A 5 triggers
   ```

### Build Failing

1. **Check build logs**:
   ```bash
   oc logs -f bc/checkin-app
   ```

2. **Check latest build status**:
   ```bash
   oc describe build $(oc get builds -l buildconfig=checkin-app --sort-by=.metadata.creationTimestamp -o name | tail -1)
   ```

3. **Manual build test**:
   ```bash
   oc start-build checkin-app --follow
   ```

### Deployment Not Updating

The Deployment uses image triggers via annotations. If the deployment doesn't update after a successful build:

1. **Check image stream**:
   ```bash
   oc get is/checkin-app
   ```

2. **Force deployment update**:
   ```bash
   oc rollout restart deployment/checkin-app
   ```

3. **Check deployment status**:
   ```bash
   oc rollout status deployment/checkin-app
   ```

## Security Notes

- Change the default webhook secret (`webhook-secret-2024`) in production
- Use repository-specific webhook URLs to prevent unauthorized builds
- Consider using GitHub App authentication for enhanced security
- Regularly rotate webhook secrets

## Multiple Environments

For multiple environments (dev, staging, prod), create separate:
- Namespaces/projects
- BuildConfigs with different webhook secrets
- GitHub webhooks (or use branch-specific triggers)

Example for staging environment:
```bash
oc new-project checkin-staging
# Deploy with modified namespace in manifests
# Set up separate GitHub webhook for staging branch
```