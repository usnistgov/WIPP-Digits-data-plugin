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

## Kubernetes deployment
**Prerequesites:**
- WIPP is deployed on the Kubernetes cluster and the WIPP Data *Permanent Volume Claim* is named `wippdata-pvc` (otherwise the name has to be changed in `wipp-digits.yaml`)
- Replace `WIPP_API_URL_VALUE` by the URL of the WIPP API (for example `"http://IP_ADDRESS:30101/api"`) in the file `wipp-digits.yaml`.  

**Deployment**

Run `kubectl apply -f wipp-digits.yaml`

WIPP Digits will be available at `http://HOST:30701` (where `HOST` is the IP address/host name of the host server).


## Notes
 
Code tested succesfully with the versions 19.10 and 20.01 of Nvidia DIGITS containers. Both classification (MNIST dataset) and segmentation (VOC2012 dataset) worked with the Caffe version. Only the classification (MNIST dataset) worked with the Tensorflow version.

**Links to WIPP**

* WIPP deployment: https://github.com/usnistgov/WIPP
* WIPP back-end: https://github.com/usnistgov/WIPP-backend
* WIPP front-end: https://github.com/usnistgov/WIPP-frontend

 
## Disclaimer

[NIST Disclaimer](LICENSE.md)