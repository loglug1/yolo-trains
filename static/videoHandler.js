document.getElementById("videoInput").addEventListener("change", handleVideoUpload);

const canvasList = [];

export async function handleVideoUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const url = URL.createObjectURL(file);
    const video = document.createElement("video");
    video.src = url;
    video.crossOrigin = "anonymous";
    video.muted = true;

    await video.play();

    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const processor = new MediaStreamTrackProcessor({ track: video.captureStream().getVideoTracks()[0] });
    const reader = processor.readable.getReader();
    const decoder = new VideoDecoder({
        output: frame => processFrame(frame, ctx, canvas),
        error: err => console.error("Decoder error:", err)
    });

    decoder.configure({
        codec: "vp9" // MKV? VP9 or H.264
    });

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        decoder.decode(value);
    }

    
    //await sendFramesToAPI();
}

function processFrame(frame, ctx, canvas) {
    ctx.drawImage(frame, 0, 0, canvas.width, canvas.height);
    const newCanvas = canvas.cloneNode(true);
    newCanvas.getContext("2d").drawImage(canvas, 0, 0);
    canvasList.push(newCanvas);
    
    document.dispatchEvent(new CustomEvent("frameExtracted", { detail: newCanvas }));

    frame.close();
}

// Convert canvas to Base64 and send it to an API
/*async function sendFramesToAPI() {
    for (const canvas of canvasList) {
        const base64Image = canvas.toDataURL("image/png");
        
        try {
            const response = await fetch("", {
                method: "POST",
                headers: { "Content-Type": "" },
                body: JSON.stringify({ image: base64Image })
            });

            if (!response.ok) throw new Error("Failed to send frame");
            console.log("Frame sent successfully");
        } catch (error) {
            console.error("Error sending frame:", error);
        }
    }
}
*/

//export { canvasList, sendFramesToAPI };
