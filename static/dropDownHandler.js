import { Video, Model } from './Classes.js'

let videos = [];

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
        populateDropdown(videos);

    } catch (error) {
        console.error('Error fetching videos:', error);
    }
}

function populateDropdown(videoArray) {
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

// Initialize on page load
document.addEventListener('DOMContentLoaded', fetchVideos);