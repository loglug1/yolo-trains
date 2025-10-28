import { Frame } from "./Classes.js";
import { fetchFrameImg } from "./api.js";

export async function updateDataPane(modelId,videoId,frame,min,max){
    console.log(`updateDataPaned ${frame}`)
    const frameNum = document.getElementById("frame-num");
    const objectListDiv = document.getElementById("object-list");
    const image = document.getElementById("frame")

    const imgSrc = await fetchFrameImg(modelId,videoId,frame.frame_num,min,max)

    image.src = imgSrc

    frameNum.innerHTML = "Frame Number: " + frame.frame_num;
    // Clear old content
    objectListDiv.innerHTML = "";

    // Loop through objects and add <p>
    frame.objects.forEach(obj => {
    const p = document.createElement("p");
    p.textContent = `${obj.object_type}, Confidence: ${obj.confidence}`;
    objectListDiv.appendChild(p);
    });
}