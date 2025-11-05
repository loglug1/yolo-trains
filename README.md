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

      * `docker compose -f compose.yaml -f compose.nvidia.yaml up` will start an instance of ROD that uses Nvidia Cuda for prediction. You will need to follow instructions [here](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) to enable Nvidia support in the Docker engine.

      * `docker compose -f compose.yaml -f compose.amd.yaml up` will start an instance of ROD that uses AMD GPUs for prediction. You will need to edit compose.amd.yaml to match settings for your chipset.

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

## Web Interface:

  * Video Input:
    1. "Video File Input" button - Select a .mp4 file for upload.
    2. "Upload" button - Uploads the selected video file to the server. The uploaded file will then be added to the "Select a video" dropdown below.
  
  * Model Input:
    1. "Model File Input" button - Select a .pt file for upload.
    2. "Upload" button - Uploads the selected model file to the server. The uploaded file will then be added to the "Select a model" dropdown below.

  * Generate Graph:
    1. Select an uploaded video from the "Select a video" dropdown.
    2. Select an uploaded model from the "Select a model" dropdown.
    3. Press "Generate Graph" to display data from the selected video-model combination on the graph.

  * Show Live Images Checkbox:
    If checked, and the video-model combination has not yet been fully processed, it will display processed frames as they are received.
  
  * Reset Zoom Button:
    Resets the zoom of the graph.

  * Min and Max:
    Updates the plotted points on the graph to be within the confidence interval based on the entered values.

  * Frames Interval: 
    Updates the plotted points to display only every X frames instead of all frames, where X is the entered value.

  * Object Dropdown:
    Plots points on the graph only if they contain the selected object. Points are plotted based on the confidence of the selected item in the frame.

  * Plotted Points:
    Represent individual frames and can be clicked to display an annotated image of that frame on the screen. The confidence values of each object detected in the selected frame will also be displayed in the data pane.
