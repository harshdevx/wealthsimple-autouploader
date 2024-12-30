#!/bin/bash
for CONTAINER in `docker ps -a | awk '{ print $1"-"$2 }'`
do

        if [ "$CONTAINER" != "CONTAINER-ID" ]; then
                CONTAINER_NAME=`echo $CONTAINER | cut -f 2 -d '-'`
                if [ "$CONTAINER_NAME" == "ws" ]; then
                        CONTAINER_ID=`echo $CONTAINER | cut -f 1 -d '-'`
                        echo "deleting container id $CONTAINER_ID..."
			docker container stop $CONTAINER_ID
			docker container rm $CONTAINER_ID
                fi
        fi
done

for IMAGE in `docker image ls | awk '{ print $1"-"$3 }'`
do
	if [ "$IMAGE" != "REPOSITORY-IMAGE" ]; then
		IMAGE_NAME=`echo $IMAGE | cut -f 1 -d '-'`
		if [ "$IMAGE_NAME" == "ws" ]; then
			IMAGE_ID=`echo $IMAGE | cut -f 2 -d '-'`
			echo "deleting image id $IMAGE_ID..."
			docker image rm $IMAGE_ID
		fi
	fi
done

git pull origin main
docker build -t ws -f Dockerfile $PWD
docker run --env-file ./src/.env ws
