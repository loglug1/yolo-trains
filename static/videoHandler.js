import { Video, Model, Frame, DetectionObject } from './Classes.js';
import { postVideo } from './api.js';




// const socket = io();

// socket.on("connect", () => {
//     console.log("Connected to server!");
//     window.annotatedVideoPlayer = new AnnotatedVideoPlayer("frame");
// });

// socket.on("test_response", (data) => {
//     console.log("Received Test Data: ", data);
//     msElapsed = Date.now() - parseInt(data);
//     console.log("Time elapsed: ", msElapsed);
// });

// socket.on("receive_annotated_frame", (dataURL) => {
//     console.log("Received Frame");
//     window.annotatedVideoPlayer.queueFrame(dataURL);
// });

function predictObjects(dataUrl) {
    socket.emit("predict_objects", dataUrl);
}

// const video = document.getElementById("videoPreview");
// const hiddenSourceCanvas = document.getElementById("hiddenSourceCanvas");
// var drawFrameInterval = Number();
// var videoURL = null;

// Video File Change
async function uploadVideo(){
  const fileInput = document.getElementById("videoInput");
  if (fileInput.files.length === 0){
    alert("Please select a video file first.");
    return;
  }

  const file = fileInput.files[0];
  const result = await postVideo(file);
  console.log("Server response:", result);
}

document.getElementById("uploadBtn").addEventListener("click",uploadVideo);

// Model File Change
// const modelFileInput = document.getElementById('modelFileInput');

// modelFileInput.addEventListener('change', () => {
//   const file = modelFileInput.files[0];

//   if (file) {
//     const formData = new FormData();
//     formData.append('modelFile', file);

//     fetch('/uploadModel', {
//       method: 'POST',
//       body: formData,
//     })
//     .then(response => {
//       if (response.ok) {
//         response.json().then(data => {alert(data['upload_status']);});
//       } else {
//         alert('File upload failed');
//       }
//     })
//     .catch(error => {
//       alert('Error uploading file:' + error);
//     });
//   }
// });