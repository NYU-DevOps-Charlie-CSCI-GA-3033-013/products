# products
Product Team for CSCI-GA.3033-013

The products resource represents the store items that the customer can buy. They could be
categorized but they donʼt have to be for this assignment. They should have a unique id
(perhaps a SKU), a name, description, price, and others attributes like perhaps an image.

[![Build Status](https://travis-ci.org/NYU-DevOps-Charlie-CSCI-GA-3033-013/products.svg?branch=master)](https://travis-ci.org/NYU-DevOps-Charlie-CSCI-GA-3033-013/products)
[![codecov](https://codecov.io/gh/NYU-DevOps-Charlie-CSCI-GA-3033-013/products/branch/master/graph/badge.svg)](https://codecov.io/gh/NYU-DevOps-Charlie-CSCI-GA-3033-013/products)


# Setting up a Vagrantfile:

1. Navigate to the your project directory in a terminal and do:
vagrant up
2. To start the VM do:
vagrant ssh
3. Navigate to the vagrant directory into your VM by doing:
cd /vagrant
4. To run the service:
python server.py
5. The app will run on
http://192.168.33.10:5000

#RESTful API calls:
In addition to the standard REST API calls (GET, PUT, POST, DELETE), the service suports the following:

1. Discontinue: an action to discontinue a product:
`PUT /products/1/discontinue`
2. Limit the result-set returned:
`GET /products?limit=5`
3. Query by attribute:
    * Query by price:  
        * `GET /products?min-price=10&max-price=20`
        * `GET /products?price=100`
    * Query by category: `GET /products?category=Electronics`
    * Query by distcontinued status: `GET /products?discontinued=true`

#Cloud Deployment:

Following are the steps to create an App on IBM Bluemix-

1. Login to your BlueMix Account
2. Create a new App
3. Choose 'Python Flask' as the boilerplate
4. Name your App and choose a unique URL for it
5. You can see the details of your App under various tabs like overview, Logs, etc.
6. To select a connection service for the App, go to 'connections' and click on 'connect new'
7. Filter the list of services by 'Data and Analytics' and select Redis Cloud
8. Note that the service is bound to this particular app
9. If asked, give the service a name
10. Scroll down the services to select the plan of your convenience, in our case, we have selected a 30 MB Free Tier that gives 1 dedicated database and 30 connections
11. It will ask you to restage the application. DO NOT restage it since the application doesn't know how to use Redis yet, so press 'Cancel'
12. Copy the following code into your vagrant file before the '#install app dependencies'. Make sure the URL in the code below contains the OS that is used by your VM.
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



# Creating docker container for the service using vagrant

1. cd into the service directory
2. type the command to install the vbguest plugin
vagrant plugin install vagrant-vbguest
3. Add the following to the vagrant file

######################################################################
  # Add Redis docker container
######################################################################
  config.vm.provision "shell", inline: <<-SHELL
    # Prepare Redis data share
    sudo mkdir -p /var/lib/redis/data
    sudo chown vagrant:vagrant /var/lib/redis/data
  SHELL

  # Add Redis docker container
  config.vm.provision "docker" do |d|
    d.pull_images "redis:alpine"
    d.run "redis:alpine",
      args: "--restart=always -d --name redis -h redis -p 6379:6379 -v /var/lib/redis/data:/data"
  end

  # Add Docker compose
  # Note: you need to install the vagrant-docker-compose or this will fail!
  # vagrant plugin install vagrant-docker-compose
  # config.vm.provision :docker_compose, yml: "/vagrant/docker-compose.yml", run: "always"
  # config.vm.provision :docker_compose, yml: "/vagrant/docker-compose.yml", rebuild: true, run: "always"
  config.vm.provision :docker_compose

  # Install Docker Compose after Docker Engine
  config.vm.provision "shell", privileged: false, inline: <<-SHELL
    sudo pip install docker-compose
    # Install the IBM Container plugin as vagrant
    sudo -H -u vagrant bash -c "echo Y | cf install-plugin https://static-ice.ng.bluemix.net/ibm-containers-linux_x64"
  SHELL

4. vagrant up
5. vagrant provision
6. vagrant ssh
7. cd /vagrant
8. vi Dockerfile

9. put the following contents into the Dockerfile.

FROM alpine:3.3

MAINTAINER NYU-Products

# Install just the Python runtime (no dev)

RUN apk add --update \
python \
py-pip \
&& rm -rf /var/cache/apk/*

ENV PORT 5000
EXPOSE $PORT

# Set up a working folder and install the pre-reqs
WORKDIR /app
ADD requirements.txt /app
RUN pip install -r requirements.txt

# Add the code as the last Docker layer because it changes the most
ADD static /app/static
ADD server.py /app

# Run the service
CMD [ "python", "server.py" ]

10. docker build -t products .
11. docker images
You should now be able to see the image 'products' in the list of docker images.
12. docker run --rm -p 5000:5000 products
This will ask you to link the redis service.
13. docker run --rm -p 5000:5000 --link redis products

You now have a docker image for your service. This image can be pushed to Bluemix as follows:

14. cf login
15. cf ic login
16. cf ic namespace set <namespace_name>
17. cf ic init
18. docker tag products registry.ng.bluemix.net/namespace_name/products
This tags the image with the tag 'latest'.
19. docker push registry.ng.bluemix.net/namespace_name/products
This will push the image to Bluemix.
20. In Bluemix, select apps and containers.
21. select 'create container'.
22. You should be able to see your image. If not, refresh/login-logout.

This image can now be linked with your service on bluemix

23. If you already have an existing service and want to link it, go to the containers and select your container directly, otherwise create a service first.
24. Select scalable in group deployment option.
25. Give the container group name.
26. Select size 64 MB, 4 GB Storage (Pico) and 2 instances.
27. Keep the host name as it is (which will be your container group name).
28. Give the port name 5000 (or whichever your service will be running on).
29. In advanced options, select the service name and then click add and create it.
30. You can see the overview and connections of your container.
31. Clicking on the application URL will take you to the service website.
