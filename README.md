# WIPP Digits Data plugin

## Login to Docker registry nvcr.io
Please refer to the Nvidia documentation: https://docs.nvidia.com/ngc/ngc-user-guide/pullcontainer.html#accessing_registry

## Build the container
`docker build . -t wipp-digits`

## Run the container
`nvidia-docker run --name wipp-digits -d -p 8888:5000 -v $WIPP_DATA_FOLDER:/data/WIPP-plugins -e WIPP_API_URL=$WIPP_API_URL wipp-digits`
* `$WIPP_API_URL` is the WIPP REST API URL (for example: http://wipp-backend:8080/api)
* `$WIPP_DATA_FOLDER` is the WIPP Data folder path on the host (for example /data/WIPP-plugins), images collections are expected to be in a sub folder called `collections`

Note: `nvidia-docker run` can be replaced by `docker run --gpus all` or `docker run --runtime=nvidia` depending on the `nvidia-docker/nvidia-docker-runtime` version installed.

## For testing - mock WIPP API
`docker run -p 9999:80 -v $PATH_TO_CURRENT_FOLDER/json-server:/data clue/json-server --routes /data/routes.json /data/db.json`
this will create a mock WIPP REST API containing mock information for two collections: digits-train-images and digits-train-masks

Run the WIPP Digits container using this mock API:
`nvidia-docker run --name wipp-digits -d -p 8888:5000 -v $WIPP_DATA_FOLDER:/data/WIPP-plugins -e WIPP_API_URL=http://localhost:9999 wipp-digits`

`$WIPP_DATA_FOLDER` is the WIPP Data folder path on the host (for example `/data/WIPP-plugins`), the sub-folder `collections` is expected to have the following structure:
```shell
├── data
│   └── WIPP-plugins
│       └── collections
│           ├── digits-train-images
│           │   └── images
│           │       ├── img_001302.ome.tif
│           │       ├── img_001823.ome.tif
│           │       ├── img_002782.ome.tif
│           │       ├── ...
│           └── digits-train-masks
│               └── images
│                   ├── img_001302.ome.tif
│                   ├── img_001823.ome.tif
│                   ├── img_002782.ome.tif
│                   ├── ...
```

