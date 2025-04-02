const socket = io();

socket.on("connect", () => {
    console.log("Connected to server!");
});

test_data = crypto.randomUUID()
console.log("Sending Test Data: ", test_data)
socket.emit("test_socket", test_data);

socket.on("test_response", (data) => {
    console.log("Received Test Data: ", data)
})

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
            const fps = 30; 
            const interval = 1000 / fps;
            const drawFrame = setInterval(() => {
                if (!video.paused && !video.ended) {
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

                    // Convert to Base64 and display in <img>
                    const base64Image = canvas.toDataURL("image/webp");
                    //console.log(base64Image); // Logs the Base64 string
                    var base64AnnotatedImage = 
                    document.getElementById("frame").src = base64Image;
                } else {
                    clearInterval(drawFrame);
                    URL.revokeObjectURL(videoURL);
                }
            }, interval);
        });
    }
});