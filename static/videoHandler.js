const socket = io();

var frameQueue = [];

socket.on("connect", () => {
    console.log("Connected to server!");
    sequenceTest();
});

socket.on("test_response", (data) => {
    console.log("Received Test Data: ", data)
    msElapsed = Date.now() - parseInt(data);
    console.log("Time elapsed: ", msElapsed);
});

socket.on("annotated_frame", (dataURL) => {
    console.log("Received Frame");
    frameQueue.push(dataURL)
});

function predictObjects(dataUrl) {
    socket.emit("predict_objects", dataUrl);
}

function sequenceTest() {
    i = 0;
    interval = 100;
    sequence = setInterval(() => {
        if (i < 20) {
            console.log("run function pls");
            testData = Date.now().toString();
            console.log("Sending Test Data: ", testData);
            socket.emit("test_socket", testData);
            i++
        } else {
            clearInterval(sequence);
        }
    }, interval);
}

document.getElementById("videoInput").addEventListener("change", function(event) {

    const file = event.target.files[0];
    if (file) {
        const videoURL = URL.createObjectURL(file);
        const video = document.getElementById("videoPreview"); // Create a hidden video element
        video.src = videoURL;
        video.playbackRate = 1.0;

        document.getElementById("videoPreview").addEventListener("play",function(){
            const canvas = document.getElementById("canvas");
            const ctx = canvas.getContext("2d");

            // Set canvas size to match video resolution
            canvas.width = 640;
            canvas.height = 360;

            // Capture frames at a steady rate (adjust FPS as needed)
            const fps = 10; 
            const interval = 1000 / fps;
            const drawFrame = setInterval(() => {
                if (!video.paused && !video.ended) {
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

                    // Convert to Base64 and display in <img>
                    const base64Image = canvas.toDataURL("image/webp");
                    predictObjects(base64Image)
                    if (frameQueue.length > 1) {
                        document.getElementById("frame").src = frameQueue.shift();
                    } else {
                        console.log("No frames to show!")
                    }
                    //console.log(base64Image); // Logs the Base64 string                    
                } else {
                    clearInterval(drawFrame);
                    URL.revokeObjectURL(videoURL);
                }
            }, interval);
        });
    }
});