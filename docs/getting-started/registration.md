# Lab Registration

Welcome to the OpenShift Demo Lab! Before you can begin the hands-on exercises, you'll need to register and get your group assignment.

## 📝 Registration Process

### Step 1: Access the Registration Portal

Visit the lab registration portal:

[**🔗 Register at register.dts-lab.fun**](https://register.dts-lab.fun)

### Step 2: Enter Your Email Address

1. Enter your **IBM email address** in the registration form
2. Click **"Check In"** to submit your registration
3. The system will validate your email against the authorized user list

!!! info "Email Validation"
    Only pre-approved IBM email addresses can register for the lab. If you receive an error, please contact your lab instructor.

### Step 3: Get Your Group Assignment

Upon successful registration, you'll receive:

- ✅ **Group Name** (e.g., "Group A", "Group B", etc.)
- ✅ **Group Letter** (A through Y - this is important for resource allocation)
- ✅ **VPC Assignment** (VPC 1 through 5)
- ✅ **Registration Timestamp**

## 🏷️ Group and VPC Mapping

The lab uses a structured group assignment system:

| Group Letters | VPC Assignment | Example Groups |
|---------------|----------------|----------------|
| **A - E** | VPC 1 | Group A, Group B, Group C, Group D, Group E |
| **F - J** | VPC 2 | Group F, Group G, Group H, Group I, Group J |
| **K - O** | VPC 3 | Group K, Group L, Group M, Group N, Group O |
| **P - T** | VPC 4 | Group P, Group Q, Group R, Group S, Group T |
| **U - Y** | VPC 5 | Group U, Group V, Group W, Group X, Group Y |

!!! tip "Remember Your Group Letter"
    Your group letter is crucial for selecting the correct resources during the lab. Make note of both your full group name and the letter.

## 🔍 Finding Your Group Information

If you need to look up your group assignment later:

1. Return to [register.dts-lab.fun](https://register.dts-lab.fun)
2. Enter your email address
3. Click **"Find My Group"** instead of "Check In"

## 👥 Group Size and Structure

- Each group contains **up to 3 participants**
- Groups are filled automatically in alphabetical order
- Group assignments are permanent for the duration of the lab

## 🗂️ Resource Organization

Your group assignment determines which resources you'll use throughout the lab:

### VPC Resources
When creating your ROKS cluster, you'll select:
- **VPC**: The VPC matching your group assignment
- **Subnets**: Subnets ending with your group letter (e.g., `lab-subnet-1-z1-ga` for Group A)

### Naming Conventions
Use consistent naming throughout the lab:
- **Cluster Name**: `roks-group-[letter]-cluster` (e.g., `roks-group-a-cluster`)
- **Project Name**: `[group-letter]-project` (e.g., `a-project`)

## ⚠️ Important Notes

!!! warning "Registration Required"
    You cannot proceed with the lab until you've completed registration and received your group assignment.

!!! note "Group Persistence"
    Your group assignment will remain the same throughout all lab sessions. Make sure to note your group letter and VPC assignment.

## 🆘 Troubleshooting Registration

### Common Issues

**"Email not found in authorized user list"**
: Your email address hasn't been pre-approved for the lab. Contact your lab instructor.

**"You have already checked in!"**
: You've already registered. The system will display your existing group assignment.

**Network/Connection Issues**
: Try refreshing the page or check your internet connection. The registration portal is hosted on IBM Cloud with high availability.

### Getting Help

If you encounter issues during registration:

1. **Double-check your email address** - Make sure it's your IBM email
2. **Contact your lab instructor** - They can verify your account status
3. **Check with fellow participants** - They may have encountered similar issues

## ✅ Next Steps

Once you've completed registration:

1. **Note your group assignment** - Write down your group letter and VPC
2. **Review the prerequisites** - Ensure you have everything needed for the lab
3. **Begin the lab sessions** - Start with [Step 1: Deploy ROKS Cluster](../lab-sessions/step-1-roks-cluster.md)

---

**Ready to continue?** 🚀 [Review Prerequisites →](prerequisites.md)