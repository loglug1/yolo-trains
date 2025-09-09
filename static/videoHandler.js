import {Video, Model, Frame, Object} from './Classes'

//HTTP GET request for all videos and models

//HTTP POST request uploading video

//HTTP POST request uploading models

//HTTP GET request for /models/model_id/video_id to populating the graph
const socket = io();

socket.on("connect", () => {
    console.log("Connected to server!");
    window.annotatedVideoPlayer = new AnnotatedVideoPlayer("frame");
});

socket.on("test_response", (data) => {
    console.log("Received Test Data: ", data);
    msElapsed = Date.now() - parseInt(data);
    console.log("Time elapsed: ", msElapsed);
});

socket.on("receive_annotated_frame", (dataURL) => {
    console.log("Received Frame");
    window.annotatedVideoPlayer.queueFrame(dataURL);
});

function predictObjects(dataUrl) {
    socket.emit("predict_objects", dataUrl);
}

// const video = document.getElementById("videoPreview");
// const hiddenSourceCanvas = document.getElementById("hiddenSourceCanvas");
const videoInput = document.getElementById("videoInput");
// var drawFrameInterval = Number();
// var videoURL = null;

videoInput.addEventListener("change", function(event) { // Register event listener for when file is 'uploaded'
    const file = event.target.files[0];
    if (file) {
        video.pause();
        
        clearInterval(drawFrameInterval);

        URL.revokeObjectURL(videoURL);
        videoURL = URL.createObjectURL(file);

        video.src = videoURL;
        video.playbackRate = 1.0;
        video.play();
    }
});

// Model File Change
const modelFileInput = document.getElementById('modelFileInput');

modelFileInput.addEventListener('change', () => {
  const file = modelFileInput.files[0];

  if (file) {
    const formData = new FormData();
    formData.append('modelFile', file);

    fetch('/uploadModel', {
      method: 'POST',
      body: formData,
    })
    .then(response => {
      if (response.ok) {
        response.json().then(data => {alert(data['upload_status']);});
      } else {
        alert('File upload failed');
      }
    })
    .catch(error => {
      alert('Error uploading file:' + error);
    });
  }
});
