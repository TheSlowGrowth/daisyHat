#!/usr/bin/env bash

DAISYHAT_CONTAINER_NAME="daisyhat-container"

echo "Usb event: $1 $2 $3 $4" >> /tmp/docker_tty.log
if [ "$1" == "added" ]
then
    docker exec --user="root" $DAISYHAT_CONTAINER_NAME mknod $2 c $3 $4
    docker exec --user="root" $DAISYHAT_CONTAINER_NAME chmod -R 777 $2
    echo "Adding $2 to docker container: $DAISYHAT_CONTAINER_NAME" >> /tmp/docker_tty.log
else
    docker exec --user="root" $DAISYHAT_CONTAINER_NAME rm $2
    echo "Removing $2 from docker container: $DAISYHAT_CONTAINER_NAME" >> /tmp/docker_tty.log
fi