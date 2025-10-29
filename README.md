# Railway Object Detection (ROD)

  If you just want to run the program, the latest build of the main branch is uploaded to Docker Hub as both [`loglug/rod:nvidia-latest`](https://hub.docker.com/repository/docker/loglug/rod/general) and [`loglug/rod:amd-latest`](https://hub.docker.com/repository/docker/loglug/rod/general).

## Building Image

  __Prerequisites:__ make sure you have Docker installed.
  
  *Note: Image has only been tested on Linux devices but possibly could work on WSL.*

  1. Clone Repository
  2. From the root of the repository, run `docker build --file Dockerfile_[amd|nvidia] --tag [Tag you would like to use]`
      * __NOTE:__ replace portions of command in \[ \] depending on your build.

## Running Image:

  There are two options for running the image:

  1. __Recommmended:__ Use Docker Compose:

      * `docker compose -f compose.yaml up` will start an instance of ROD that uses the CPU for prediction.

      * `docker compose -f compose.yaml -f compose.amd.yaml up` will start an instance of ROD that uses AMD GPUs for prediction. You will need to edit compose.amd.yaml to match settings for your chipset.

      * Full Nvidia support inside Docker containers is a WIP.

      * You can add `IMAGE=[CUSTOM DOCKER IMAGE]` to the beginning of either Docker Compose commands to pass in a custom built image from the previous section.

      * __Note:__ The default compose files also start an instance of InfluxDB to test integration. If you would like to use an external instance of InfluxDB, you can configure the connection using the environment variables found in compose.yaml.

  2. Run the container using `docker run --name rod -p 5000:5000 --mount type=volume,source=rod-data,target=/uploads loglug/rod:nvidia-latest python app.py`
      * See compose files for environment variables to configure program.
      * `loglug/rod:nvidia-latest` can be replaced with a custom Docker image built in the previous section.
  3. __Unsupported:__ Install python3.13 with pip and use `requirements.txt` to install dependencies. Then use `python app.py` to start the program. You can use any environment variables found in the compose files to configure the program.

## Using the program:

  The program can be accessed at http://<ROD_HOSTNAME>:<ROD_PORT> (Likely http://localhost:5000 by default.)

  __NOTE:__ The url listed in the console upon startup is internal to the Docker container.

## Environment Variables:

   The Docker container can be configured using environment variables. See `compose.yml` for the currently available environment variables.

## API:
  
  ROD has a REST API that can be used with third party apps. See `api_reference.txt` for a list of available endpoints. (WIP)

