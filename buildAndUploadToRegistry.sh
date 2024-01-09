#!/usr/bin/env bash

# build image
IMAGE=registry.datexis.com/mmenke/bvg-scraper

version=0.0.13
echo "Version: $version"
docker build --platform linux/amd64 -t $IMAGE -t $IMAGE:$version .
docker push $IMAGE:$version
echo "Done pushing image $image for build $version"