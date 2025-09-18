import { Video, Model, Frame, DetectionObject } from './Classes.js';
import { fetchProcessing } from './api.js';

export async function getFrames(videoId, modelId) {
    if (!videoId || !modelId) {
        throw new Error("Both videoId and modelId are required.");
    }

    try {
        // Fetch data from the backend
        const data = await fetchProcessing(videoId, modelId);

        if (!data) {
            console.error("No data returned from fetchProcessing.");
            return [];
        }

        // Ensure `frames` exists in response
        if (!Array.isArray(data.frames)) {
            console.error("Invalid data format: 'frames' key missing or not an array.");
            return [];
        }

        // Convert JSON data into Frame and DetectionObject instances
        const frameObjects = data.frames.map(frameData => {
            const objects = frameData.objects.map(obj => 
                new DetectionObject(
                    obj.type,
                    obj.x1,
                    obj.x2,
                    obj.y1,
                    obj.y2,
                    obj.confidence
                )
            );

            return new Frame(frameData.frame_num, objects, frameData.connection_id);
        });

        console.log("Processed frames:", frameObjects);
        return frameObjects;

    } catch (error) {
        console.error("Error fetching frames:", error);
        return [];
    }
}

document.addEventListener("DOMContentLoaded", () => {
  const ctx = document.getElementById("tempScatterChart").getContext("2d");

  // Chart data container
  const tempData = [];

  // Create Chart.js line chart
  const tempScatterChart = new Chart(ctx, {
    type: "line",
    data: {
      datasets: [
        {
          label: "Object confidence per frame",
          data: tempData,
          pointBackgroundColor: "red",
          borderColor: "red",
          pointRadius: 5
        }
      ]
    },
    options: {
      responsive: true,
      scales: {
        x: {
          type: "linear",
          title: {
            display: true,
            text: "Frames"
          }
        },
        y: {
          title: {
            display: true,
            text: "Confidence"
          },
          min: 0,
          max: 1 // confidence values are between 0 and 1
        }
      }
    }
  });

  let socket = null;

  // Function to initialize WebSocket connection
  function initializeWebSocket(connectionId) {
    // Use wss:// for secure connection or ws:// for local development
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    socket = new WebSocket(`${wsProtocol}//${window.location.host}/ws/${connectionId}`);

    socket.onopen = () => {
      console.log(`WebSocket connected for connection ID: ${connectionId}`);
    };

    socket.onmessage = (event) => {
      const frameData = JSON.parse(event.data);
      console.log("Received WebSocket frame:", frameData);

      // Process incoming frame
      const objects = frameData.objects.map(obj => 
        new DetectionObject(
          obj.type,
          obj.x1,
          obj.x2,
          obj.y1,
          obj.y2,
          obj.confidence
        )
      );

      const frame = new Frame(frameData.frame_num, objects, frameData.connection_id);

      // Update chart with new frame data
      updateChartWithFrame(frame);
    };

    socket.onclose = () => {
      console.log("WebSocket connection closed");
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
  }

  // Function to update chart with a single frame
  function updateChartWithFrame(frame) {
    if (!frame.objects.length) return;

    const targetObjectType = tempScatterChart.data.datasets[0].label.split(' ')[0] || frame.objects[0].object_type;

    frame.objects.forEach(obj => {
      if (obj.object_type === targetObjectType) {
        tempScatterChart.data.datasets[0].data.push({
          x: frame.frame_num,
          y: obj.confidence
        });
      }
    });

    // Sort data by frame number to ensure proper ordering
    tempScatterChart.data.datasets[0].data.sort((a, b) => a.x - b.x);
    tempScatterChart.update();
  }

  // Fetch frames and plot data
  async function addDataPoints() {
    const videoDropdown = document.getElementById("videoDropdown");
    const modelDropdown = document.getElementById("modelDropdown");

    const videoId = videoDropdown.value;
    const modelId = modelDropdown.value;

    if (!videoId || !modelId) {
      alert("Please select both a video and a model.");
      return;
    }

    // Reset existing data
    tempScatterChart.data.datasets[0].data = [];
    tempScatterChart.data.datasets[0].label = "Object confidence per frame";
    tempScatterChart.update();

    // Fetch and process frames
    const frames = await getFrames(videoId, modelId);

    if (frames.length === 0) {
      alert("No frames were returned from the server.");
      return;
    }

    console.log("Frames retrieved:", frames);

    // Check for connection_id in any frame to initialize WebSocket
    const frameWithConnectionId = frames.find(frame => frame.connection_id);
    if (frameWithConnectionId) {
      initializeWebSocket(frameWithConnectionId.connection_id);
    }

    // Find the first object type in the first frame that has objects
    const firstFrameWithObjects = frames.find(frame => frame.objects.length > 0);

    if (!firstFrameWithObjects) {
      alert("No objects found in any frame.");
      return;
    }

    const targetObjectType = firstFrameWithObjects.objects[0].object_type;
    console.log("Target object type:", targetObjectType);

    // Filter and map frames for that object type
    const filteredData = [];
    frames.forEach(frame => {
      frame.objects.forEach(obj => {
        if (obj.object_type === targetObjectType) {
          filteredData.push({
            x: frame.frame_num,     // Frame number on x-axis
            y: obj.confidence       // Confidence on y-axis
          });
        }
      });
    });

    console.log("Filtered data for graph:", filteredData);

    // Update chart with filtered data
    tempScatterChart.data.datasets[0].data = filteredData;
    tempScatterChart.data.datasets[0].label = `${targetObjectType} Confidence per Frame`;
    tempScatterChart.update();
  }

  // Attach the function to the button
  document.getElementById("addDataBtn").addEventListener("click", addDataPoints);
});