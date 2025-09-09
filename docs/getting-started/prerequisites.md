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

## 🛠️ Recommended Tools

### Essential Tools

| Tool | Purpose | Installation |
|------|---------|-------------|
| **Web Browser** | Access IBM Cloud console and OpenShift web console | Any modern browser |
| **OpenShift CLI (`oc`)** | Command-line operations | [Download from Red Hat](https://docs.openshift.com/container-platform/latest/cli_reference/openshift_cli/getting-started-cli.html) |
| **IBM Cloud CLI** | Manage IBM Cloud resources | [Installation Guide](https://cloud.ibm.com/docs/cli?topic=cli-install-ibmcloud-cli) |

### Optional Tools

| Tool | Purpose | When You'll Need It |
|------|---------|-------------------|
| **kubectl** | Kubernetes-native operations | Advanced troubleshooting |
| **curl** | API testing and debugging | API exploration |
| **git** | Clone demo repositories | Local development |
| **Docker** | Local container testing | Local development |

### Installing OpenShift CLI

=== "macOS"

    ```bash
    # Using Homebrew
    brew install openshift-cli
    
    # Or download directly
    curl -LO https://mirror.openshift.com/pub/openshift-v4/clients/ocp/stable/openshift-client-mac.tar.gz
    tar -xzf openshift-client-mac.tar.gz
    sudo mv oc /usr/local/bin/
    ```

=== "Linux"

    ```bash
    # Download and install
    curl -LO https://mirror.openshift.com/pub/openshift-v4/clients/ocp/stable/openshift-client-linux.tar.gz
    tar -xzf openshift-client-linux.tar.gz
    sudo mv oc /usr/local/bin/
    ```

=== "Windows"

    1. Download from [OpenShift CLI Releases](https://mirror.openshift.com/pub/openshift-v4/clients/ocp/stable/)
    2. Extract the ZIP file
    3. Add `oc.exe` to your PATH

### Installing IBM Cloud CLI

=== "macOS"

    ```bash
    # Using Homebrew
    brew install ibm-cloud-cli
    
    # Or using installer
    curl -fsSL https://clis.cloud.ibm.com/install/osx | sh
    ```

=== "Linux"

    ```bash
    # Using installer
    curl -fsSL https://clis.cloud.ibm.com/install/linux | sh
    ```

=== "Windows"

    1. Download installer from [IBM Cloud CLI](https://cloud.ibm.com/docs/cli?topic=cli-install-ibmcloud-cli)
    2. Run the installer
    3. Follow installation prompts

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

## 🌐 Network Requirements

### Internet Access
- ✅ **Stable internet connection** for accessing IBM Cloud and GitHub
- ✅ **Access to IBM Cloud domains** (`*.cloud.ibm.com`)
- ✅ **Access to Red Hat domains** (`*.openshift.com`, `*.redhat.com`)
- ✅ **Access to GitHub** (`github.com`) for demo applications

### Firewall Considerations
Ensure your network allows:
- **HTTPS (443)** for all web console access
- **SSH (22)** if using terminal access to cluster nodes
- **Custom ports** for OpenShift routes (typically handled automatically)

## 💻 Browser Compatibility

### Supported Browsers
- ✅ **Chrome** 90+ (Recommended)
- ✅ **Firefox** 88+
- ✅ **Safari** 14+
- ✅ **Edge** 90+

### Browser Settings
- ✅ **JavaScript enabled** (required for OpenShift web console)
- ✅ **Cookies enabled** (for authentication sessions)
- ✅ **Pop-up blockers disabled** for IBM Cloud domains

## 📋 Pre-Lab Checklist

Before starting the lab, verify you have:

### Account Setup
- [ ] IBM Cloud account login credentials
- [ ] Completed lab registration at [register.dts-lab.fun](https://register.dts-lab.fun)
- [ ] Group assignment and VPC information noted

### Tool Installation
- [ ] OpenShift CLI (`oc`) installed and in PATH
- [ ] IBM Cloud CLI installed (optional but recommended)
- [ ] Modern web browser with JavaScript enabled

### Environment Verification
- [ ] Stable internet connection
- [ ] Access to IBM Cloud console
- [ ] Firewall/proxy allows access to required domains

### Knowledge Check
- [ ] Basic understanding of containers
- [ ] Comfortable with web-based interfaces
- [ ] Familiar with YAML file format

!!! success "Ready to Begin!"
    Once you've completed this checklist, you're ready to start the lab!

## 🔍 Verification Commands

Test your tool installations:

```bash
# Check OpenShift CLI
oc version --client

# Expected output: Client Version: 4.x.x
```

```bash
# Check IBM Cloud CLI (if installed)
ibmcloud version

# Expected output: ibmcloud version 2.x.x
```

```bash
# Verify internet connectivity
curl -I https://cloud.ibm.com

# Expected: HTTP 200 response
```

## 🆘 Getting Help

If you're missing prerequisites:

1. **Contact your lab instructor** - They can help with account access issues
2. **Check with IT/Network teams** - For firewall or network issues
3. **Review installation guides** - For tool installation problems
4. **Ask fellow participants** - They may have solved similar issues

---

**All set?** 🎉 [Start with Lab Registration →](registration.md)