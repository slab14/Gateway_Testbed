#!/bin/bash

close_exited_docker_containers() {
    sudo docker rm $(sudo docker ps -aqf status=exited)
}

# Delete Exited Docker Containers
close_exited_docker_containers
