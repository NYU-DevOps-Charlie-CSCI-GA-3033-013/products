# products
Product Team for CSCI-GA.3033-013

The products resource represents the store items that the customer can buy. They could be
categorized but they donʼt have to be for this assignment. They should have a unique id
(perhaps a SKU), a name, description, price, and others attributes like perhaps an image.


Cloud Deployment:

Following are the steps to create an App on IBM Bluemix-

1. Login to your BlueMix Account
2. Create a new App
3. Choose 'Python Flask' as the boilerplate
4. Name your App and choose a unique URL for it
5. You can see the various details of your App under various tabs like overview, Logs, etc.
6. To select a connection service for the App, go to 'connections' and click on 'connect new'
7. Filter the list of services by 'Data and Analytics' and select Redis Cloud
8. Note that the service is bound to this particular app
9. If asked, give the service a name
10. Scroll down the services to select the plan of your convenience, in our case, we have selected a 30 MB Free Tier that gives 1 dedicated database and 30 connections
11. It will ask you to restage the application. DO NOT restage it since the applications doesn't know how to use Redis yet, so press 'Cancel'
12. Copy the following code into your vagrant file under 'Setup a Python Development Environment', before the '#instato download the CF CLI'. Make sure the URL in the code below contains the OS that is used by your VM.
    Our VM uses Ubutu hence the release is debian64

# Install the Cloud Foundry CLI
    wget -O cf-cli-installer_6.24.0_x86-64.deb 'https://cli.run.pivotal.io/stable?release=debian64&version=6.24.0&source=github-rel'
    sudo dpkg -i cf-cli-installer_6.24.0_x86-64.deb
    rm cf-cli-installer_6.24.0_x86-64.deb


**** MANUAL DEPLOYMENT ****

13. Edit the `manifest.yml` file and change the name of the application to something unique.
14. Then from a terminal login into Bluemix and set the api endpoint to the Bluemix region you wish to deploy to:

cf login -a api.ng.bluemix.net

15. The login will ask you for you `email`(username) and `password`, plus the `organisation` and `space` if there is more than one to choose from.
16. From the root directory of the application code execute the following to deploy the application to Bluemix.

 cf push <YOUR_APP_NAME> -m 64M

To deploy with a different hostname to the app name:

cf push <YOUR_APP_NAME> -m 64M -n <YOUR_HOST_NAME>

17. Once the application is deployed and started open a web browser and point to the application route defined at the end of the `cf push` command i.e. http://<APP NAME>.mybluemix.net/. This will execute the code under the `/` app route defined in the `server.py` file. Navigate to `/products` to see a list of products returned as JSON objects.

18. Make sure the route directory contains the following files-

 **Procfile** - Contains the command to run when you application starts on Bluemix. It is represented in the form `web: <command>` where `<command>` in this sample case is to run the `py` command and passing in the the `server.py` script.
In our case, it will contain- web: python server.py

**requirements.txt** - Contains the external python packages that are required by the application. These will be downloaded from the [python package index](https://pypi.python.org/pypi/) and installed via the python package installer (pip) during the buildpack's compile stage when you execute the cf push command. In this sample case we wish to download the [Flask package](https://pypi.python.org/pypi/Flask) at version 0.12 and [Redis package](https://pypi.python.org/pypi/Redis) at version greater than or equal to 2.10
In our case, it will contain- Flask==0.12

**manifest.yml** - Controls how the app will be deployed in Bluemix and specifies memory and other services like Redis that are needed to be bound to it.

**server.py** - the python application script.

**** AUTOMATIC DEPLOYMENT ****

This is done by creating a pipeline and connecting it to our GitHub Organization

13. On your Bluemix App, got to 'Overview' and scroll down to continuous delivery and click on 'Enable' to enable CD Toolchain which includes GitHub Integration, DevOps Pipeline, deployment to Bluemix, and a WEB IDE
In case you're using a Git Organization, the enable button won't work since it only shows personal Repos. Hence you need to create a CD Pipeline manually in the following way-

14. Go to the dashboard and click on 'Continuous Delivery' under services, if it doesn't show CD then create a new Service and select 'Continuous Delivery' under DevOps filter
15. Start with a pipeline and select 'Cloud Foundry' as the template, and use the APP NAME for Pipeline Name and Application Name. Also give a name to the toolchain.
16. Scroll down to Source code and select your Git Organization name and press 'Create'. You now have a Pipeline
connected to your organization repo in GitHub.


In case you're Using Git Repos, do the following steps-

14. Scroll down on the next page to give the name of the toolchain.
15. Select Repository Type as Existing and then select your Organization on GitHub as the Source Repo URL
16. Select the 'Delivery Pipeline' in the next page
17. Edit the manifest.yml file to change the name and host of the app to the name provisioned in your Bluemix and push back the changes. This will automatically kick off the DevOps Pipeline
18. When both the build and deploy stage have completed successfully, you can launch your newly deployed App and also have a look at the runtie log



