# Step 2: OpenShift Console Tour

Now that your ROKS cluster is running, it's time to explore the OpenShift web console and understand the different views and capabilities available to you.

!!! info "Estimated Time"
    **Exploration Time:** 20-25 minutes

## 🎯 Learning Objectives

By the end of this step, you will:

- ✅ Navigate between Administrator and Developer console views
- ✅ Understand the purpose of different console sections
- ✅ Create your first project namespace
- ✅ Explore deployment options available in OpenShift

## 📋 Prerequisites

- [ ] Completed [Step 1: Deploy ROKS Cluster](step-1-roks-cluster.md)
- [ ] ROKS cluster showing "Normal" status
- [ ] Access to OpenShift web console

## 🖥️ Accessing the OpenShift Console

### 1. Open the Web Console

1. From your cluster details page in IBM Cloud console
2. Click **"OpenShift web console"** 
3. You'll be automatically logged in with your IBM Cloud credentials

### 2. Initial Console View

Upon first access, you'll see the **Administrator** view dashboard featuring:
- **Cluster overview** with resource utilization
- **Recent events** and activity
- **Quick access** to documentation
- **Alert status** and notifications

## 🔧 Administrator View Exploration

The Administrator view provides cluster-wide management capabilities.

### Key Navigation Sections

#### 1. Home
- **Projects** - Namespace management
- **Search** - Resource discovery across the cluster
- **Events** - Cluster-wide event monitoring
- **API Explorer** - Kubernetes API documentation

#### 2. Workloads
- **Pods** - Individual container instances
- **Deployments** - Application deployment management
- **StatefulSets** - Stateful application management
- **DaemonSets** - Node-level service deployment

#### 3. Networking
- **Services** - Internal load balancing
- **Ingress** - External traffic routing
- **Routes** - OpenShift-specific external access
- **Network Policies** - Traffic control between pods

#### 4. Storage
- **Persistent Volumes** - Cluster-wide storage resources
- **Persistent Volume Claims** - Storage requests from applications
- **Storage Classes** - Types of available storage

#### 5. Observe
- **Alerting** - Cluster health alerts
- **Metrics** - Prometheus-based monitoring
- **Logging** - Centralized log viewing
- **Events** - Detailed event tracking

#### 6. Compute
- **Nodes** - Worker node management
- **Machine Sets** - Node scaling configuration
- **Machine Config** - Node configuration management

!!! tip "Administrator vs Developer"
    Administrator view is for cluster-wide operations and infrastructure management. Developer view focuses on application development and deployment.

## 👨‍💻 Developer View Exploration

Switch to Developer view using the perspective switcher in the top-left corner.

### Developer Console Features

The Developer view is designed for application developers and includes:

#### 1. Project Selection
- **Current project** displayed prominently
- **Project switcher** for navigating between namespaces
- **Create project** option

#### 2. Main Navigation

**+Add**
: Deploy new applications and services

**Topology**
: Visual representation of your applications

**Project**
: Project-specific resources and settings

**Builds**
: Source-to-Image builds and build configurations

**Pipelines**
: CI/CD pipeline management

**Helm**
: Helm chart deployment and management

## 📁 Creating Your First Project

A project in OpenShift is equivalent to a Kubernetes namespace with additional security and resource management features.

### 1. Create a New Project

1. In Developer view, click **"Create a project"** 
2. **Project Details:**
   - **Name:** `[group-letter]-project` 
     - Example: `a-project` for Group A
     - Example: `m-project` for Group M
   - **Display Name:** `Group [Letter] Demo Project`
   - **Description:** `OpenShift demo lab project for Group [Letter]`

3. Click **"Create"**

### 2. Verify Project Creation

- Your new project should appear in the project selector
- The topology view should be empty (no applications yet)
- Project details should show in the Project tab

## 🛠️ Exploring Deployment Options

With your project created, explore the available deployment options.

### 1. Access the +Add Page

Click **"+Add"** in the Developer navigation to see deployment options:

#### Developer Catalog
- **Samples** - Pre-built example applications
- **Services** - Databases and middleware
- **Operators** - Advanced service management

#### Import Options
- **Import from Git** - Deploy from source code repositories
- **Container Images** - Deploy from existing container images
- **YAML** - Deploy from Kubernetes manifests

#### Advanced Options
- **Operator Backed** - Deploy via OpenShift operators
- **Helm Charts** - Package manager for Kubernetes
- **Event Source** - Serverless event-driven applications

### 2. Explore Sample Applications

1. Click **"Samples"** to see available templates
2. Browse options like:
   - Node.js applications
   - Python Django/Flask apps
   - Java Spring Boot applications
   - Database templates

### 3. Check Available Container Images

1. Click **"Container Images"** 
2. Note that you can deploy from:
   - Public registries (Docker Hub, Quay.io)
   - Private registries
   - OpenShift internal registry

## 🔍 Understanding the Interface

### Topology View Concepts

The Topology view will become your primary interface for managing applications:

- **Nodes** represent applications or services
- **Connectors** show relationships between components
- **Status indicators** show health and deployment status
- **Groupings** organize related resources

### Resource Management

OpenShift provides several ways to manage resources:
- **Console forms** - User-friendly web interfaces
- **YAML editor** - Direct Kubernetes resource editing
- **Command line** - Via `oc` CLI tool

## 🎓 Key Concepts Learned

### OpenShift Architecture
- **Projects/Namespaces** provide isolation and resource management
- **Role-Based Access Control (RBAC)** controls who can access what
- **Routes vs Services** - External vs internal network access

### Console Navigation
- **Administrator view** - Cluster-wide operations and monitoring
- **Developer view** - Application-focused development workflow
- **Context switching** between different operational perspectives

### Deployment Patterns
- **Source-to-Image (S2I)** - Build from source code
- **Container deployment** - Deploy existing images
- **Template-based** - Repeatable deployment patterns

## ✅ Verification Checklist

You've successfully completed Step 2 when:

- ✅ You can navigate between Administrator and Developer views
- ✅ You've explored the main sections of both console views
- ✅ You've created a project with your group naming convention
- ✅ You've reviewed available deployment options in +Add
- ✅ You understand the different ways to deploy applications

## 🔍 Optional Exploration

If you have extra time, explore these additional features:

### Administrator View Deep Dive
- Check **Node** information in Compute section
- Review **Storage Classes** available
- Look at **Events** to see cluster activity

### Developer View Features
- Explore **Helm** charts available
- Check **Builds** section (currently empty)
- Review **Project** settings and resource quotas

## 📝 What's Next?

Now that you're comfortable with the OpenShift console, you're ready to deploy your first application!

In **Step 3**, you'll:
- 🚀 Deploy Demo App V1 using "Import from Git"
- 📊 Learn about ephemeral storage characteristics
- 🔍 Explore Source-to-Image (S2I) builds
- 📈 Monitor application resources and performance

---

**Ready to deploy your first app?** 🚀 [Continue to Step 3: Deploy Demo App V1 →](step-3-demo-app-v1.md)