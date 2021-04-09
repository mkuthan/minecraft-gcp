#!/bin/bash

gsutil -m rsync -x ".*\.log\.gz$" -r ${bucket} /var/minecraft

docker run -d --name mc --rm=true \
  -p 25565:25565 \
  -v /var/minecraft:/data \
  -e EULA=TRUE \
  -e VERSION=${minecraft_version} \
  -e MEMORY=3G  \
  itzg/minecraft-server:latest