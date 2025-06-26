# openEHRTool

A tool meant to make it easier to interact with a **EHRBase** server. This is the version 2 of openEHRTool. The old one can be found at https://github.com/crs4/openEHR-tool

| Version | Sync/Async | Frontend | Backend | Redis use |
| ------  | ---- | -------- | ------- | ----- | 
|   1     | Synchronous | HTML,JS,Bootstrap | Flask | Activity log |
|   2     | Asynchronous | Vue | FastAPI | Activity log, Caching of artefacts id |

# How to install and run

### &#x1F335; Docker "All in One" &#x1F335;
If you don't already have a working ehrbase server you can opt for the docker compose script that runs all the applications(EHRBase, openEHRTool and Redis) in the same docker subnet.

#### Steps

Add to /etc/hosts the following lines:
```
127.0.0.1	frontend.localhost
127.0.0.1	backend.localhost
```
Build the images. From the root directory of the project run:
```
docker buildx bake -f compose-total.yml
```
then start the services:
```
docker compose -f compose-total.yml up -d
```
Now open the browser and type the address:
```
http://frontend.localhost
```
In the login mask type a username and password for a user already registered in EHRBase. The server address will be http://ehrbase:8080/erhbase/

For instance, recalling the default user in EHRBase:
```
username:  ehrbase-user
password:  SuperSecretPassword
server url: http://ehrbase:8080/erhbase/
```

_Note_: The compose-total file adopts EHRBase version 2.15.0 . That is the latest version of EHRBase tested with the tool. 

### &#x1F335; Docker "Separated" &#x1F335;
EHRBase is run in a network/docker-compose separated from openEHRTool.

#### Steps
Copy the .env.ehrbase file to the directory where the EHRBase compose file is located.
Start EHRBase.
```
docker compose up -d
```
 Let's suppose it is running at host localhost:8080
 
Add to /etc/hosts the following lines:
```
127.0.0.1	frontend.localhost
127.0.0.1	backend.localhost
```
Build the images. From the root directory of the project run:
```
docker buildx bake
```
then start the services:
```
docker compose up -d
```
Now open the browser and type the address:
```
http://frontend.localhost
```
In the login mask choose a username and password for a user already registered in EHRBase. 
To get the server address find the bridge ip
```
docker network inspect bridge --format='{{(index .IPAM.Config 0).Gateway}}'
```
output will be something like 172.17.0.1 . The server url will be then:
```
http://172.17.0.1:8080/erhbase/
```
For instance, recalling the default user in EHRBase:
```
username:  ehrbase-user
password:  SuperSecretPassword
server url: http://172.17.0.1:8080/erhbase/
```
## &#x1F335; Installing and running locally&#x1F335;

### Frontend

Install node js for your OS. For instance, for linux:
```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
\. "$HOME/.nvm/nvm.sh"
nvm install 22
```
clone the project:
```
https://github.com/sasurfer/openEHRTool-v2.git
```
Go to to the frontend directory:
```
cd openEHRTool-v2/frontend-vue
```
install the required packages:
```
npm install
```
run the server with:
```
npm run serve
```

### Backend

#### Redis
Go to the redis directory. From the root directory of the project run:
```
cd redis
```
start the redis server:
```
redis-server ./redis.conf

```
#### FastAPI


Install python 3.11 or greater and pip. Then go to the backend directory. From the root directory of the project run:
```
cd backend-fastapi
```
create a virtual environment:
```
python3 -m venv venv
source venv/bin/activate

```
install the required packages:
```
pip install -r requirements.txt
```
Now you can start the backend:
```
python -m app
```

# Settings

## EHRBase
For EHRBase use/modify the environment file .env.ehrbase found in the root directory of the project.

## Redis
For Redis use the environment file .redis.con found in the redis directory of the project.

## Frontend
In frontend-vue/src/config.js the default for the backend is set. Usually you don't have to change it.

## Backend
In app/configuration/openehrtool.cfg are defined the redis hostname and port and the EHRBase nodename. Usually you don't have to change them.



# Acknowledgments

This work has been partially funded by the following sources:

 <ul>
<li>   the “Total Patient Management” (ToPMa) project (grant by the Sardinian Regional Authority, grant number RC_CRP_077). Intervento finanziato con risorse FSC 2014-2020 - Patto per lo Sviluppo della Regione Sardegna;
<li>the “Processing, Analysis, Exploration, and Sharing of Big and/or Complex Data” (XDATA) project (grant by the Sardinian Regional Authority).  -->
