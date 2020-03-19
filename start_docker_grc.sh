#!/usr/bin/env bash
# usage: start_grc_docker.sh <app under apps/ to run in GRC>
IMG_NAME=bse/gr-equisat_decoder-maint3.7

git submodule update --init --recursive

docker build -t $IMG_NAME .
docker run -it --rm \
    --name gr-equisat_decoder \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e DISPLAY=$DISPLAY \
    -v $(pwd)/apps:/root/gr-equisat_decoder/apps/ \
    $IMG_NAME \
    $1