# Step 1: Deploy ROKS Cluster

In this first lab session, you'll create your Red Hat OpenShift on IBM Cloud (ROKS) cluster. This cluster will be your foundation for all subsequent demo applications and exercises.

!!! info "Estimated Time"
    **Setup Time:** 10-15 minutes  
    **Provisioning Time:** 10-15 minutes (cluster creation is automated)

## 🎯 Learning Objectives

By the end of this step, you will:

- ✅ Understand ROKS cluster architecture and components
- ✅ Successfully create a ROKS cluster using IBM Cloud console
- ✅ Configure proper networking and security settings for the lab
- ✅ Verify cluster deployment and access

## 📋 Prerequisites

Before starting this step:

- [ ] Completed [lab registration](../getting-started/registration.md)
- [ ] Have your **group letter** and **VPC assignment** noted
- [ ] Access to IBM Cloud console
- [ ] Basic understanding of Kubernetes concepts

## 🚀 Step-by-Step Instructions

### 1. Access IBM Cloud Console

1. Navigate to [IBM Cloud](https://cloud.ibm.com)
2. Log in with your IBM credentials
3. Go to **Containers** → **Clusters**

Direct link: [https://cloud.ibm.com/containers/cluster-management/clusters](https://cloud.ibm.com/containers/cluster-management/clusters)

### 2. Initiate Cluster Creation

Click the **"Create Cluster"** button to begin the setup process.

### 3. Configure Basic Settings

#### Orchestrator Selection
- **Orchestrator:** Select **Red Hat OpenShift**

!!! tip "Why OpenShift?"
    Red Hat OpenShift provides enterprise-grade Kubernetes with additional developer and operational tools, making it ideal for production workloads.

#### Infrastructure Type
- **Infrastructure:** Select **VPC**

### 4. Network Configuration

#### Virtual Private Cloud
- **Virtual private cloud:** Select the VPC that matches your group assignment

| Group Letters | VPC to Select |
|---------------|---------------|
| A - E | VPC 1 | tech-labs-vpc-1 | 
| F - J | VPC 2 | tech-labs-vpc-2 | 
| K - O | VPC 3 | tech-labs-vpc-3 | 
| P - T | VPC 4 | tech-labs-vpc-4 | 
| U - Y | VPC 5 | tech-labs-vpc-5 | 

#### Location and Subnets
- **Location:** Use the pre-selected region (ca-tor for our lab)
- **Subnets:** Select the subnet for each zone that ends with your group letter

**Example for Group A:**
- Zone 1: Select `subnet-zone-1-group-a`
- Zone 2: Select `subnet-zone-2-group-a`
- Zone 3: Select `subnet-zone-3-group-a`

!!! warning "Important"
    Make sure to select subnets that end with **your specific group letter**. Using incorrect subnets may cause networking conflicts.

### 5. OpenShift Version and Licensing

#### Version Configuration
- **OpenShift version:** Leave as default (latest stable version)
- **OpenShift Container Platform (OCP) license:** No changes needed

### 6. Worker Pool Configuration

#### Default Worker Pool
- **Worker nodes:** Scale down to **1 node per zone** for a total of **3 workers**
- **Worker node flavor:** Leave as default (4 vCPUs, 16GB RAM recommended)

!!! note "Cost Optimization"
    We're using fewer nodes for the lab to optimize costs while still demonstrating all key concepts.

#### Encryption Settings
- **Worker pool encryption:** **Disable** this feature for the lab

### 7. Network and Registry Settings

#### Network Settings
- **Network settings:** No changes needed (use defaults)

#### Internal Registry
- **Internal registry:** Select the **lab COS instance** from the dropdown

### 8. Security Configuration

#### Outbound Traffic Protection
- **Outbound traffic protection:** **Disable** this feature for the lab
- Accept the confirmation pop-up when prompted

#### Cluster Encryption
- **Cluster Encryption:** **Disable** this feature for the lab

#### Ingress Secrets Management
- **Ingress secrets management:** 
  - Select the **demo lab Secrets Manager instance**
  - Choose the **tech-demo-lab-0825 Secrets Manager group**

#### VPC Security Groups
- **VPC security groups:** No changes needed (use defaults)

### 9. Cluster Identification

#### Cluster Details
- **Cluster name:** `roks-group-[letter]-cluster`
  - Example: `roks-group-a-cluster` for Group A
  - Example: `roks-group-m-cluster` for Group M
- **Resource group:** Select **Default**

!!! tip "Naming Convention"
    Use consistent naming throughout the lab to make resource management easier.

### 10. Integrations and Monitoring

#### Activity Tracking
- **Activity tracking:** No changes needed (default is fine)

#### Logging
- **Logging:** **Disable** this feature for the lab

#### Monitoring
- **Main monitoring:** Leave **enabled**
- **Workload Protection:** **Disable** this feature for the lab

### 11. Review and Create

#### Cost Review
- Expected cost should be approximately **$600/month**
- This is for demonstration purposes only - clusters will be deleted after the lab

#### Final Review
Review all settings to ensure they match your group assignment:
- ✅ Correct VPC selected
- ✅ Correct subnets for your group letter
- ✅ 3 worker nodes total (1 per zone)
- ✅ Proper naming convention used

#### Create Cluster
Click **"Create"** to start the provisioning process.

## ⏳ Waiting for Cluster Provisioning

### What Happens Next?

1. **Initial Setup** (1-2 minutes): IBM Cloud validates your configuration
2. **Infrastructure Provisioning** (5-10 minutes): VPC resources are allocated
3. **OpenShift Installation** (5-10 minutes): OpenShift is installed on the infrastructure
4. **Final Configuration** (2-3 minutes): Networking and security are configured

### While You Wait

This is a perfect time to:
- ☕ Refill your coffee or water
- 📚 Review the [OpenShift documentation](https://docs.openshift.com/)
- 💬 Discuss container orchestration concepts with fellow participants
- 🧠 Take a bio break

!!! info "Normal Wait Time"
    Cluster provisioning typically takes 10-15 minutes. This is normal for enterprise-grade Kubernetes clusters.

## ✅ Verification Steps

Once your cluster shows **"Normal"** status:

### 1. Check Cluster Status
- In the IBM Cloud console, verify your cluster shows **"Normal"** state
- All worker nodes should show **"Ready"** status

### 2. Access OpenShift Web Console
- Click **"OpenShift web console"** from your cluster details page
- You should see the OpenShift login page

### 3. Verify Cluster Information
In the OpenShift console, check:
- **Cluster version** is displayed correctly
- **Node count** shows 3 nodes
- **Storage classes** are available

## 🎯 Key Concepts Learned

### Infrastructure as Code
- **VPC Architecture:** Understanding how clusters integrate with VPC networking
- **Resource Organization:** How IBM Cloud organizes compute, network, and storage resources

### OpenShift Architecture
- **Control Plane:** Master nodes managed by IBM (invisible to users)
- **Worker Nodes:** Where your applications will run
- **Networking:** How pods communicate within the cluster and externally

### Security Considerations
- **Network Isolation:** VPC provides network-level security
- **RBAC:** Role-Based Access Control for user permissions
- **Secrets Management:** Integration with IBM Secrets Manager

## 🔍 Troubleshooting

### Common Issues

**"No subnets available for my group"**
: Verify you're looking in the correct VPC for your group assignment. Each VPC contains subnets for specific groups.

**"Cluster creation failed"**
: Check that you have the necessary permissions in IBM Cloud. Contact your lab instructor if permissions issues persist.

**"Cost estimate seems high"**
: The $600/month estimate is for continuous operation. Lab clusters will only run for a few hours and then be deleted.

### Getting Help

If you encounter issues:
1. **Take a screenshot** of any error messages
2. **Note your group letter and VPC assignment**
3. **Ask your lab instructor** for assistance
4. **Check with neighboring participants** who may have solved similar issues

## 🎉 Success Criteria

You've successfully completed Step 1 when:

- ✅ Cluster status shows **"Normal"** in IBM Cloud console
- ✅ All worker nodes show **"Ready"** status
- ✅ You can access the OpenShift web console
- ✅ OpenShift console displays cluster information correctly

## 📝 What's Next?

With your ROKS cluster running, you're ready for **Step 2: OpenShift Console Tour**.

In the next step, you'll:
- 🖥️ Explore the OpenShift web console interface
- 🔄 Switch between Administrator and Developer views
- 📁 Create your first project namespace
- 🛠️ Review available deployment options

---

**Cluster ready?** 🚀 [Continue to Step 2: Console Tour →](step-2-console-tour.md)