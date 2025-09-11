//HTTP POST request uploading video
export async function postVideo(video){
    try {
        const formData = new FormData();
        //Must match Falsk's request.files['video_file']
        formData.append("video_file",video);

        const response = await fetch("http://127.0.0.1:5000/videos", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error('Upload failed: ${response.status');
        }

        const result = await response.json();
        console.log("Upload success:",result);
        return result;
    } catch (error) {
        console.error("Error uploading video:", error);
    }
}

//HTTP POST request uploading models .pt files

//HTTP GET request for /models/model_id/video_id to populating the graph

//HTTP GET request for all videos and models