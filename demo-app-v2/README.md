# Demo App Version 2

Follow this guide to deploy our demo app to OpenShift with persistent storage. 

## Steps

### Deploying the second demo app

You should end up on the `default` project dashboard. If not, select `default` from the project dropdown in the upper left hand corner of the page. Click on `Add` in the left hand navigation to start the app deployment process.

![Add new app](../images/roks-add-app.png)

- Click the `Import from Git` option
    - Git Repo URL: https://github.com/cloud-design-dev/tech-lab-demos.git
	    - Expand `Show Advanced Git options`
		    - Git reference: No changes needed
			- Context dir: `/demo-app-v2`
			- Source Secret: No changes needed
	- Dockerfile build and deploy configuration
	    - General:
		    - Application name: `<group-name>-demo-apps`
			- Name: `demoapp2`
		- Build: No changes needed
		- Deploy: No changes needed
		- Advanced Options:
			- Target Port: Select `8080` from the dropdown
			- Expand Show advanced Routing options
			    - Ensure that Secure Route is selected, TLS Termination is set to Edge, and Insecure Traffic is set to Redirect
				- All other settings can be left as is 
		- Click Create to start the build and deploy of the demo app
	- You should be taken to the Topology view of the `default` project where you can see the build and deployment process
		- Under Build section, click `View Logs` to look at Build Logs
        - Once the build is complete, you should see a green check mark next to the build icon
		- Click back to Topology view
		    - Show Running pods
			- Click Route link to visit the demo app  
			- Test persistence (it should know retain the count even after refreshing the page)

## Demo Flow Comparison

### V1 (In-Memory)
1. Click "Test Persistence" → Creates memory entry
2. Click "Reload Page" → All data lost (ID resets to 1)

### V2 (Database)  
1. Click "Test Persistence" → Creates database entry
2. Click "Reload Page" → Data persists! (ID continues incrementing)
3. Shows total database entries and connection type

## OpenShift Resources

### PostgreSQL Deployment
- **Secret**: Database credentials (demo/demo_password)
- **PVC**: 1GB persistent volume for database storage
- **Deployment**: PostgreSQL 15 container with resource limits
- **Service**: Internal database service on port 5432

### V2 App Deployment  
- **Deployment**: App container with DATABASE_URL environment variable
- **Service**: HTTP service on port 8080
- **Route**: Secure HTTPS route with edge TLS termination
- **BuildConfig**: Builds app image from GitHub Dockerfile
