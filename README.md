# minecraft-gcp

Minecraft Server automation on GCP, for my son and his friends.

Features:
* Secured server status/start/stop pages (served by [Cloud Functions](https://cloud.google.com/functions/docs))
* Automated server shutdown if there is no active players (scheduled by [Cloud Scheduler](https://cloud.google.com/scheduler/docs))
* Minecraft [RCON](https://wiki.vg/RCON) password secured in [Google Secret Manager](https://cloud.google.com/secret-manager/docs)
* Minecrart world synchronized to/from [Google Storage](https://cloud.google.com/storage/docs)

TODO list:
* Compute instance cost reduction
* OAuth [authentication](https://cloud.google.com/functions/docs/securing/authenticating)
* Docker image with Minecraft Server
* DNS

## Usage

Server status page.

[https://your-project.cloudfunctions.net/server_status?api_key=super_secret_key](https://your-project.cloudfunctions.net/server_status?api_key=super_secret_key)

Start server.

[https://your-project.cloudfunctions.net/start_server?api_key=super_secret_key](https://your-project.cloudfunctions.net/start_server?api_key=super_secret_key)

Stop server.

[https://your-project.cloudfunctions.net/stop_server?api_key=super_secret_key](https://your-project.cloudfunctions.net/stop_server?api_key=super_secret_key)


## Local environment

Use the `venv` command to create a virtual copy of the entire Python installation. 

```shell
python -m venv venv
```

Set your shell to use the `venv` paths for Python by activating the virtual environment.

```shell
source venv/bin/activate
```

Install packages (see [pre-installed packages](https://cloud.google.com/functions/docs/writing/specifying-dependencies-python) for recommended versions).

```shell
pip install -r requirements.txt
```

## Google Cloud

Update components.

```shell
gcloud components update
```

Configure default projects.

```shell
gcloud config set project minecraft-272917
```

Enable App Engine Admin API.

```shell
gcloud services enable appengine.googleapis.com
```

Create service account for Terraform.

```shell
gcloud iam service-accounts create terraform
```

Assign mandatory roles for created service account.

```shell
gcloud projects add-iam-policy-binding minecraft-272917 \
  --member="serviceAccount:terraform@minecraft-272917.iam.gserviceaccount.com" \
  --role="roles/storage.admin"
gcloud projects add-iam-policy-binding minecraft-272917 \
  --member="serviceAccount:terraform@minecraft-272917.iam.gserviceaccount.com" \
  --role="roles/cloudfunctions.admin"
gcloud projects add-iam-policy-binding minecraft-272917 \
  --member="serviceAccount:terraform@minecraft-272917.iam.gserviceaccount.com" \
  --role="roles/compute.admin"
gcloud projects add-iam-policy-binding minecraft-272917 \
  --member="serviceAccount:terraform@minecraft-272917.iam.gserviceaccount.com" \
  --role="roles/pubsub.admin"
gcloud projects add-iam-policy-binding minecraft-272917 \
  --member="serviceAccount:terraform@minecraft-272917.iam.gserviceaccount.com" \
  --role="roles/cloudscheduler.admin"
gcloud projects add-iam-policy-binding minecraft-272917 \
  --member="serviceAccount:terraform@minecraft-272917.iam.gserviceaccount.com" \
  --role="roles/appengine.appAdmin"
```

Service account needs to be a member of the Compute Engine default service account. 

```shell
gcloud iam service-accounts add-iam-policy-binding minecraft-272917@appspot.gserviceaccount.com \
  --member="serviceAccount:terraform@minecraft-272917.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

Generate service account key.

```shell
gcloud iam service-accounts keys create minecraft-terraform.json \
  --iam-account=terraform@minecraft-272917.iam.gserviceaccount.com
```

Copy downloaded key into clipboard and set GitHub secret GCP_SA_KEY, paste the key from the clipboard.

```shell
pbcopy < minecraft-terraform.json
```

Remove the key.

```shell
rm minecraft-terraform.json
```

## Github

Set up GitHub secret GCP_PROJECT_ID.


## Secret manager

Create secret for RCON.

```shell script
gcloud secrets create "rcon" --replication-policy="automatic"
```

Add secret version.

```shell script
echo -n "this is my super rcon secret" | \
    gcloud secrets versions add "rcon" --data-file=-
```

Create secret for cloud functions api key.

```shell script
gcloud secrets create "api" --replication-policy="automatic"
```

Add secret version.

```shell script
echo -n "this is my super api secret" | \
    gcloud secrets versions add "api" --data-file=-
```

## Cloud functions

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
  --source=./cloud-function --runtime=python38 --trigger-http 
```

Start server page.

```shell script
gcloud functions deploy start_server \
  --timeout=300s --max-instances=1 \
  --region=europe-west1 \
  --stage-bucket=minecraft-272917-cloud-functions \
  --source=./cloud-function --runtime=python38 --trigger-http
```

Stop server page.

```shell script
gcloud functions deploy stop_server \
  --timeout=300s --max-instances=1 \
  --region=europe-west1 \
  --stage-bucket=minecraft-272917-cloud-functions \
  --source=./cloud-function --runtime=python38 --trigger-http
```

Automated server stopping handler.

```shell script
gcloud functions deploy stop_server_handler \
  --timeout=300s --max-instances=1 \
  --region=europe-west1 \
  --stage-bucket=minecraft-272917-cloud-functions \
  --source=./cloud-function --runtime=python38 --trigger-topic ten-minutes-jobs
```

Disable built-in authentication for HTTP cloud functions.

```shell script
gcloud alpha functions add-iam-policy-binding server_status --region=europe-west1 --member=allUsers --role=roles/cloudfunctions.invoker
```

```shell script
gcloud alpha functions add-iam-policy-binding stop_server --region=europe-west1 --member=allUsers --role=roles/cloudfunctions.invoker
```

```shell script
gcloud alpha functions add-iam-policy-binding start_server --region=europe-west1 --member=allUsers --role=roles/cloudfunctions.invoker
```
