# minecraft-gcp

Minecraft Server automation on GCP

Features:
* Server status/start/stop pages (served by [Cloud Functions](https://cloud.google.com/functions/docs))
* Automated server shutdown if there is no active players (scheduled by [Cloud Scheduler](https://cloud.google.com/scheduler/docs))
* Minecraft [RCON](https://wiki.vg/RCON) password secured in [Google Secret Manager](https://cloud.google.com/secret-manager/docs)
* Minecrart world synchronized to/from [Google Storage](https://cloud.google.com/storage/docs)

TODO list:
* Docker image instead of startup-script / shutdown-script
* DNS
* Compute instance cost reduction

## Local environment

Use the `venv` command to create a virtual copy of the entire Python installation. 

```shell script
python -m venv venv
```

Set your shell to use the `venv` paths for Python by activating the virtual environment.

```shell script
source venv/bin/activate
```

Install packages (see [pre-installed packages](https://cloud.google.com/functions/docs/writing/specifying-dependencies-python) for recommended versions).

```shell script
pip install -r cloud-function/requirements.txt
```

## Secret manager

TODO

## Cloud scheduler

Create an App Engine app within the current Google Cloud Project.

```shell script
gcloud app create --region=europe-west
```

Create PubSub topic for scheduled events.

```shell script
gcloud pubsub topics create ten-minutes-jobs
```

Schedule events published to PubSub topic every ten minutes.

```shell script
gcloud scheduler jobs create pubsub ten-minutes-jobs \
  --schedule "*/10 * * * *" --topic ten-minutes-jobs --message-body " "
```

Cron job could be paused and resumed.

```shell script
gcloud scheduler jobs pause ten-minutes-jobs
```

```shell script
gcloud scheduler jobs resume ten-minutes-jobs
```

## Google storage

TODO: setup bucket and configure minecraft distro

## Compute instance

TODO:
https://cloud.google.com/solutions/gaming/minecraft-server

Startup script.

```shell script
#! /bin/bash

# install java & screen
apt-get update && apt-get install -y default-jre-headless screen

# install minecraft from GS
mkdir -p /minecraft

gsutil -m rsync -x ".*\.log\.gz$" -r gs://minecraft-272917 /minecraft

# start minecraft
cd /minecraft
screen -d -m -S mcs java -Xms1G -Xmx3G -d64 -jar server.jar nogui
```

Shutdown script.

```shell script
#! /bin/bash

# stop minecraft 
screen -r mcs -X stuff '/stop\n'

# save minecraft installation to GS
gsutil -m rsync -x ".*\.log\.gz$" -r /minecraft gs://minecraft-272917
```

## Cloud functions

Create stage bucket for cloud functions.

```shell script
gsutil mb -c regional -l europe-west1 gs://minecraft-272917-cloud-functions
```

Add `secretmanager.secretAccessor` role to service account.

```shell script
TODO
```

Deploy cloud functions (see [deploy manual](https://cloud.google.com/sdk/gcloud/reference/functions/deploy)).

Server status page.

```shell script
gcloud functions deploy server_status \
  --timeout=180s --max-instances=1 \
  --region=europe-west1 \
  --stage-bucket=minecraft-272917-cloud-functions \
  --source=./cloud-function --runtime=python37 --trigger-http 
```

Start server page.

```shell script
gcloud functions deploy start_server \
  --timeout=300s --max-instances=1 \
  --region=europe-west1 \
  --stage-bucket=minecraft-272917-cloud-functions \
  --source=./cloud-function --runtime=python37 --trigger-http
```

Stop server page.

```shell script
gcloud functions deploy stop_server \
  --timeout=300s --max-instances=1 \
  --region=europe-west1 \
  --stage-bucket=minecraft-272917-cloud-functions \
  --source=./cloud-function --runtime=python37 --trigger-http
```

Automated server stopping handler.

```shell script
gcloud functions deploy stop_server_handler \
  --timeout=300s --max-instances=1 \
  --region=europe-west1 \
  --stage-bucket=minecraft-272917-cloud-functions \
  --source=./cloud-function --runtime=python37 --trigger-topic ten-minutes-jobs
```
