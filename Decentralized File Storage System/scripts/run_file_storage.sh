#!/bin/bash

original_directory=$(pwd)

cd "$(dirname "$0")"

cd ../

TRACKER_HOST="localhost"
TRACKER_PORT=60000
PEER_PORTS=(50110 50111 50112)
HTTP_PORTS=(5001 5002 5003)

pids=()

echo -e "\e[1;36mStarting the tracker...\e[0m"
python -m blocktubes.tracker $TRACKER_PORT &
pids+=($!)
sleep 2

echo -e "\e[1;36mStarting the peers and Flask web applications...\e[0m"
for i in "${!PEER_PORTS[@]}"
do
    peer_port=${PEER_PORTS[$i]}
    http_port=${HTTP_PORTS[$i]}
    echo -e "\e[1;33mStarting peer on port $peer_port and Flask on port $http_port...\e[0m"
    #python -m blocktubes.peer $peer_port --tracker_host $TRACKER_HOST --tracker_port $TRACKER_PORT &
    pids+=($!)
    export PEER_PORT=$peer_port
    FLASK_APP=decentralized_file_storage/app.py flask run --port=$http_port &
    pids+=($!)
    sleep 2
done

read -p "$(echo -e "\e[1;34mPress [ENTER] to stop the decentralized file storage system...\e[0m")"

echo -e "\e[1;31mStopping the processes...\e[0m"
for pid in "${pids[@]}"
do
    kill -9 $pid
done

echo -e "\e[1;32mDecentralized file storage system stopped.\e[0m"

cd "$original_directory"
