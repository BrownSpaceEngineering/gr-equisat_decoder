#!/usr/bin/env bash
# see https://github.com/fcwu/docker-ubuntu-vnc-desktop for how to access GRC
# basically, go to: http://localhost:8080 after launching this
IMG_NAME=brownspaceengineering/gr-equisat_decoder:maint-3.7

git submodule update --init --recursive

docker build -t $IMG_NAME .
docker run -it --rm \
    --name gr-equisat_decoder \
    -p 8080:80 \
    -p 5900:5900 \
    -v $(pwd)/apps:/root/gr-equisat_decoder/apps/ \
    $IMG_NAME
    # to use with GQRX UDP: add --net=host