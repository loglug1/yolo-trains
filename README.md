# Railway Object Detection (ROD)

  If you just want to run the program, the latest build of the main branch is uploaded to Docker Hub as both [`loglug/rod:nvidia-latest`](https://hub.docker.com/repository/docker/loglug/rod/general) and [`loglug/rod:amd-latest`](https://hub.docker.com/repository/docker/loglug/rod/general).

## Building Image

  __Prerequisites:__ make sure you have Docker installed.
  
  *Note: Image has only been tested on Linux devices but possibly could work on WSL.*

  1. Clone Repository
  2. From the root of the repository, run `docker build --file Dockerfile_[amd|nvidia] --tag [Tag you would like to use]` -- __NOTE:__ replace portions of command in \[ \] depending on your build.

## Running Image:

  There are two options for running the image:

  1. Make a copy/edit ```compose.yml``` found in the root of the repository and use ```docker compose up``` to start the app. By default, this file builds from the Docker Hub version of the app. If you would like to use your own build, change the image for rod to the tag that you created in step 2 of Building Image. -- __Note:__ This compose file also starts an instance of InfluxDB to test the integration with ROD.
  2. Run the container using `docker run --name rod -p 5000:5000 --env ROD_ALLOWED_ORIGINS=http://localhost:5000 --mount type=volume,source=rod-data,target=/uploads loglug/rod:nvidia_latest python app.py`

## Using the program:

  The program can be accessed at http://<ROD_HOSTNAME>:<ROD_PORT> (Likely http://localhost:5000 by default.)
  __NOTE:__ The url listed in the console upon startup is internal to the Docker container.

## Environment Variables:

   The Docker container can be configured using environment variables. See `compose.yml` for the currently available environment variables.

## API:
  
  ROD has a REST API that can be used with third party apps. See `api_reference.txt` for a list of available endpoints. (WIP)

