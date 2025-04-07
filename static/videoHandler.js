class AnnotatedVideoPlayer {
    constructor(imgID) {
        this.frameQueue = [];
        this.imgElement = document.getElementById(imgID)
    }

    play() {
        const fps = 10; 
        const interval = 1000 / fps;
        var skippedFrames = 0;
        this.annotatedPlayer = setInterval(() => {
            if (this.frameQueue.length > 0) {
                for (var i = 0; i <= skippedFrames && this.frameQueue.length > 0; i++) { // Display the number of skipped frames + the current frame
                    console.log("displayed frame");
                    this.imgElement.src = this.frameQueue.shift();
                }
            } else {
                skippedFrames++;
                console.log("queue empty");
            }
        }, interval);
    }
    
    pause() {
        clearInterval(this.annotatedPlayer);
    }

    clearQueue() {
        this.frameQueue = [];
    }

    queueFrame(frame) {
        this.frameQueue.push(frame);
    }
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

document.getElementById("videoInput").addEventListener("change", function(event) {

    const file = event.target.files[0];
    if (file) {
        const videoURL = URL.createObjectURL(file);
        const video = document.getElementById("videoPreview"); // Create a hidden video element
        video.src = videoURL;
        video.playbackRate = 1.0;

        document.getElementById("videoPreview").addEventListener("play",function(){
            const hiddenSourceCanvas = document.getElementById("hiddenSourceCanvas");
            const ctx = hiddenSourceCanvas.getContext("2d");

            // Set canvas size to match video resolution
            hiddenSourceCanvas.width = 640;
            hiddenSourceCanvas.height = 360;

            // Capture frames at a steady rate (adjust FPS as needed)
            const fps = 10; 
            const interval = 1000 / fps;
            const drawFrame = setInterval(() => {
                if (!video.paused && !video.ended) {
                    ctx.drawImage(video, 0, 0, hiddenSourceCanvas.width, hiddenSourceCanvas.height);

                    // Convert to Base64 and display in <img>
                    const base64Image = hiddenSourceCanvas.toDataURL("image/webp");
                    predictObjects(base64Image)
                    //console.log(base64Image); // Logs the Base64 string                    
                } else {
                    if (video.ended) {
                        URL.revokeObjectURL(videoURL);
                    }
                    window.annotatedVideoPlayer.pause();
                    clearInterval(drawFrame);
                }
            }, interval);
            window.annotatedVideoPlayer.play();
        });

        video.play();
    }
});