# Prerequisites

Before beginning the OpenShift Demo Lab, ensure you have the necessary access, tools, and knowledge to complete the exercises successfully.

## 🔐 Required Access

### IBM Cloud Account
- ✅ **IBM Cloud account** with appropriate permissions
- ✅ **Access to create ROKS clusters** in the assigned VPC
- ✅ **Resource group access** (typically "Default")
- ✅ **Container Registry permissions** for the lab COS instance

### Lab Resources
- ✅ **Pre-provisioned VPC infrastructure** (provided by lab instructors)
- ✅ **Subnet allocations** for your assigned group
- ✅ **Secrets Manager instance** for certificate management
- ✅ **Container Object Storage** for internal registry

!!! info "Resource Provisioning"
    Lab instructors have pre-provisioned the VPC infrastructure, subnets, and supporting services. You'll use these during cluster creation.

## 🛠️ Required Tools

### Essential Tools

#### Recommended approach

It is recommended to use [IBM Cloud Shell](https://cloud.ibm.com/docs/cloud-shell?topic=cloud-shell-shell-ui) for the lab exercises, as it comes pre-installed with necessary tools like `kubectl`, `ibmcloud` and `oc` as well as ibmcloud cli plugins for container service and container registry.

To open Cloud Shell, click the IBM Cloud Shell icon in the IBM Cloud console. A session starts and automatically logs you in to the IBM Cloud CLI with your current account.

#### Alternative

If you prefer to work from your local machine, ensure you have the following tools installed:

| Tool | Purpose | Installation |
|------|---------|-------------|
| **OpenShift CLI (`oc`)** | Command-line operations | [Download from Red Hat](https://docs.openshift.com/container-platform/latest/cli_reference/openshift_cli/getting-started-cli.html) |
| **IBM Cloud CLI** | Manage IBM Cloud resources | [Installation Guide](https://cloud.ibm.com/docs/cli?topic=cli-install-ibmcloud-cli) |
| **git** | Clone demo repositories | Local development |

#### Optional Tools

| Tool | Purpose | When You'll Need It |
|------|---------|-------------------|
| **kubectl** | Kubernetes-native operations | Advanced troubleshooting |
| **curl** | API testing and debugging | API exploration |
| **Docker** | Local container testing | Local development |

## 📚 Knowledge Prerequisites

### Required Knowledge

**Container Basics**
: Understanding of what containers are and basic container concepts

**Web Applications**
: Familiarity with web applications and HTTP/HTTPS

**Command Line**
: Basic comfort with terminal/command prompt operations

**YAML Files**
: Ability to read and understand YAML configuration files

### Helpful Background

**Kubernetes Concepts**
: Knowledge of pods, services, and deployments (not required but helpful)

**Database Basics**
: Understanding of relational databases like PostgreSQL

**DevOps Practices**
: Familiarity with CI/CD concepts

**Cloud Computing**
: General understanding of cloud services and infrastructure

!!! tip "Learning as You Go"
    Don't worry if you're not familiar with all these concepts! The lab is designed to teach you as you progress through the exercises.

## 📋 Pre-Lab Checklist

Before starting the lab, verify you have:

### Account Setup

- [ ] IBM Cloud account login credentials
- [x] Completed lab registration
- [ ] Group assignment and VPC information noted

!!! success "Ready to Begin!"
    Once you've completed this checklist, you're ready to start the lab!

## 🆘 Getting Help

If you're missing prerequisites:

1. **Contact your lab instructor** - They can help with account access issues
2. **Check with IT/Network teams** - For firewall or network issues
3. **Review installation guides** - For tool installation problems
4. **Ask fellow participants** - They may have solved similar issues

---

## 🚀 Next Steps

[Start the Lab Sessions](../lab-sessions/overview.md) - Begin your OpenShift journey!
