# Demo Lab

## User Walkthrough

### Step 1: Deploy ROKS cluster

- Login to Cloud dashboard and navigate to https://cloud.ibm.com/containers/cluster-management/clusters
- Click Create Cluster
    - Orchestrator: Select Red Hat OpenShift
	- Infrastructure: Select VPC
	- Virtual private cloud: Select the VPC that matches your group from the drop down. 
	- Location: Select the subnet for each zone that ends in your group letter. For instance group `a` would select `lab-subnet-1-z1-ga` for zone 1 and `lab-subnet-1-z2-ga` for zone 2, and so on.
	- OpenShift version: No changes needed
	- OpenShift Container Platform (OCP) license: No changes needed
	- Worker pool: Scale down default worker pool to 1 node per zone for a total of 3 workers
	- Worker pool encryption: Disable this feature for the lab
	- Network settings: No changes needed
	- Internal registry: Select the lab COS instance
	- Security:
		- Outbound traffic protection: Disable this feature for the lab. You will be presented will a pop-up to accept the change.
		- Cluster Encryption: Disable this feature for the lab
		- Ingress secrets management: Select the demo lab Secrets Manager instance and the tech-demo-lab-0825 Secrets Manager group.
		- VPC security groups: No changes needed
	- Cluster details:
		- Cluster name: roks-group--cluster
		- Resource group: Default
	- Integrations:
		- Activity tracking: No changes needed
		- Logging: Disable this feature for the lab
		- Monitoring: Leave main select enabled, disable the Workload Protection feature.
	- Review Cluster configuration
		- Cost should show as roughly $600/mo
		- Click Create to start the provisioning process
		- Refill on water, caffeine or take a bio break. Cluster provision time is roughly 10 minutes

### Step 2: Initial ROKS dashboards overview
- Administrator view
	- From the cloud portal cluster view, click OpenShift web console to login to the OpenShift console
	- Explore the default administrator homepage (events view, handy docs, alerts)
	- Click through the following navigation tabs: Workloads, Networks, Observe, Compute)
	- Scroll back to top of dashboard and change the view from Administrator to Developer
- Developer view
	- Click Create a Project and give the project a name like -project
	- Explore the projects quick start templates and OCP catalog options
		- Developer catalog
		- Samples
		- Container Images
		- Import from Git

### Step 3: Create demo app from Github repo using
- Click the Import from Git option
	- Git Repo URL: https://github.com/greyhoundforty/tech-labs-dallas
		- Expand Show Advanced Git options
			- Git reference: No changes needed
			- Context dir: `demo-app-v1`
			- Source Secret: No changes needed
- Dockerfile build and deploy configuration
	- General:
		- Application name: <group-name>-demo-apps
		- Name: demoapp1
	- Build: No changes needed
	- Deploy: No changes needed
	- Advanced Options:
		- Target Port: Select 8080 from the dropdown
		- Expand Show advanced Routing options
			- Ensure that Secure Route is selected, TLS Termination is set to Edge, and Insecure Traffic is set to Redirect
			- All other settings can be left as is
	- Click Create to start the build and deploy of the demo app
- Topology view
	- Under Build section, click View Logs to look at Build Logs
	- Click back to Topology view
		- Show Running pods
		- Click Route link to visit the demo app

### Step 4: Add Persistence to the demo app
- Click the Import from Git option
	- Git Repo URL: https://github.com/greyhoundforty/tech-labs-dallas
		- Expand Show Advanced Git options
			- Git reference: No changes needed
			- Context dir: `demo-app-v2`
			- Source Secret: No changes needed
- Dockerfile build and deploy configuration
	- General:
		- Application name: <group-name>-demo-apps
		- Name: demoapp2
	- Build: No changes needed
	- Deploy: No changes needed
	- Advanced Options:
		- Target Port: Select 8080 from the dropdown
		- Expand Show advanced Routing options
			- Ensure that Secure Route is selected, TLS Termination is set to Edge, and Insecure Traffic is set to Redirect
			- All other settings can be left as is
	- Click Create to start the build and deploy of version 2 of the demo app
- Postgres as the database
    - Persistent Volume Claim (PVC) for the database
    - Explain PVs/PVCs (will show on demo app)
- Show events view and storage view in Administrator panel

### Step 5:
- Add resource limits and scaling config
- Invoke traffic script to show HPA scaling deployment
