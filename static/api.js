import { Video, Model,Frame,DetectionObject } from "./Classes.js";

//=====POST=========================================================================

//HTTP POST request uploading video
export async function postVideo(video){
    try {
        const formData = new FormData();
        //Must match Falsk's request.files['video_file']
        formData.append("video_file",video);

        const response = await fetch("/videos", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Upload failed: ${response.status}`);
        }

        const result = await response.json();
        console.log("Upload success:",result);
        return result;
    } catch (error) {
        console.error("Error uploading video:", error);
    }
}

//HTTP POST request uploading models .pt files
export async function postModel(modelFile){
    try {
        const formData = new FormData();
        formData.append("model_file",modelFile);

        const response = await fetch("/models", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Upload failed: ${response.status}`);
        }

        const result = await response.json();
        console.log("Model upload success:",result);
        return result;
    } catch (error) {
        console.error("Error uploading model:", error);
    }
}


//=====GET======================================================================

export async function fetchVideos() {
    try {
        const response = await fetch('/videos', { method: 'GET' });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        // Parse the JSON response
        const data = await response.json();

        // Convert each item into a Video object
        let videos = data.map(video => new Video(video.title, video.video_id));

        return videos;

    } catch (error) {
        console.error('Error fetching videos:', error);
        //ensure its iterable
        return[];
    }
}

export async function fetchModels() {
    try {
        const response = await fetch('/models', { method: 'GET' });
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        // Parse the JSON response
        const data = await response.json();

        // Convert each item into a Video object
        let models = data.map(model => new Model(model.title, model.model_id));

        return models;

    } catch (error) {
        console.error('Error fetching models:', error);
        return [];
    }
}

// /models/<model_id>/<video_id>/<frame_number>
//frame_num: 0
// image: "data:image/webp;base64,UklGRtSgAABXRUJQVlA4IMigAA
// objects:
export async function fetchFrameImg(modelId,videoId,frameNum){
    try {
        const response = await fetch(`/models/${modelId}/${videoId}/${frameNum}`);

        if(!response.ok){
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        //Parse the JSON response
        const data = await response.json();
        return data.image
    }catch(error){
        console.error('Error fetching processed frame image:', error);
        return null;
    }

}

// HTTP GET request for /models/model_id/video_id to populating the graph
// This should get frames, might need different response based on if already processed or not
export async function fetchProcessing(videoId,modelId){
    try {
        const response = await fetch(`/models/${modelId}/${videoId}`, {methods: 'GET'});

        if(!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        //Parse the JSON response
        const data = await response.json();
        return data;
    }catch(error){
        console.error('Error fetching processed frames:', error);
        return null;
    }
}

//HTTP Get 
