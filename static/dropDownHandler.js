import { Video, Model } from './Classes.js'

let videos = [];
let models = [];

export async function fetchVideos() {
    try {
        const response = await fetch('/videos', { method: 'GET' });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        // Parse the JSON response
        const data = await response.json();

        // Convert each item into a Video object
        videos = data.map(video => new Video(video.title, video.video_id));

        // Populate the dropdown
        populateVideoDropdown(videos);

    } catch (error) {
        console.error('Error fetching videos:', error);
    }
}

function populateVideoDropdown(videoArray) {
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
        option.value = video.title;   
        dropdown.add(option);
    });
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
        models = data.map(model => new Model(model.model_title, model.model_id));

        // Populate the dropdown
        populateModelDropdown(models);

    } catch (error) {
        console.error('Error fetching models:', error);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', fetchVideos);
document.addEventListener('DOMContentLoaded', fetchVideos);