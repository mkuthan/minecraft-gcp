#!/bin/bash

gsutil -m rsync -x ".*\.log\.gz$" -r ${bucket} /var/minecraft

minecraft_rcon_password=$(gcloud secrets versions access latest --secret=rcon)

docker run -d --name mc --rm=true \
  -p ${minecraft_port}:${minecraft_port} \
  -p ${rcon_port}:${rcon_port}
  -v /var/minecraft:/data \
  -e EULA=TRUE \
  -e VERSION=${minecraft_version} \
  -e MEMORY=3G  \
  -e ENABLE_RCON="true" \
  -e RCON_PORT=${rcon_port}
  -e RCON_PASSWORD="\$minecraft_rcon_password" \
  itzg/minecraft-server:latest