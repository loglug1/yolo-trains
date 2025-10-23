import { Video, Model, Frame, DetectionObject } from './Classes.js';
import { postVideo, postModel, fetchVideos, fetchModels, fetchProcessing } from './api.js';



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

// function predictObjects(dataUrl) {
//     socket.emit("predict_objects", dataUrl);
// }

// Video File Change
document.getElementById("videoInput").addEventListener("change", function() {
  const label = document.getElementById("videoLabel");
  if(this.files.length > 0){
    //update label text to selected file name
    label.textContent = this.files[0].name;
  }else{
    //Reset label if no file is selected
    label.textContent = "File Input";
  }
})
// Uploading video
async function uploadVideo(){
  const fileInput = document.getElementById("videoInput");
  if (fileInput.files.length === 0){
    alert("Please select a video file first.");
    return;
  }

  const file = fileInput.files[0];
  const result = await postVideo(file);
  console.log("Server response:", result);
  alert(`Server response: ${result}`);
  populateVideoDropdown();
}

async function uploadModel(){
  const fileInput = document.getElementById("modelInput");
  if (fileInput.files.length === 0){
    alert("Please select a model file first.");
    return;
  }

  const file = fileInput.files[0];
  const result = await postModel(file);
  console.log("Server response:", result);
  alert(`Server response: ${result}`);
  populateModelDropdown();
}

document.getElementById("uploadBtn").addEventListener("click",uploadVideo);

async function populateVideoDropdown() {
    let videoArray = await fetchVideos();
    const dropdown = document.getElementById('videoDropdown');

    // Clear any existing options
    dropdown.innerHTML = '';

    // Add a default placeholder option
    const defaultOption = document.createElement('option');
    defaultOption.text = 'Select a video';
    defaultOption.value = '';
    dropdown.add(defaultOption);

    // Add video options where both value and text are the title
    videoArray.forEach(video => {
        const option = document.createElement('option');
        option.text = video.title;    // Displayed text
        option.value = video.video_id;   // Underlying value
        dropdown.add(option);
    });
}

// Model File Change

async function populateModelDropdown() {
    let modelArray = await fetchModels();
    const dropdown = document.getElementById('modelDropdown');

    // Clear any existing options
    dropdown.innerHTML = '';

    // Add a default placeholder option
    const defaultOption = document.createElement('option');
    defaultOption.text = 'Select a model';
    defaultOption.value = '';
    dropdown.add(defaultOption);

    // Add video options where both value and text are the title
    modelArray.forEach(model => {
        const option = document.createElement('option');
        option.text = model.model_title;    // Displayed text
        option.value = model.model_id;   // Underlying value
        dropdown.add(option);
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', populateVideoDropdown);
document.addEventListener('DOMContentLoaded', populateModelDropdown);
