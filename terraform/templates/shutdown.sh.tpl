#!/bin/bash

docker exec -i mc rcon-cli stop

gsutil -m rsync -x ".*\.log\.gz$" -r /var/minecraft ${bucket}
