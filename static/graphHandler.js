import { Video, Model, Frame, DetectionObject } from './Classes.js';
import { fetchProcessing } from './api.js';

var frames = [];
var liveObjectTypes = new Set(); // To track unique object types in live mode
var currentObjectType = null;    // Currently selected object type
var socket = null;               // Socket connection
var tempScatterChart = null;

export async function getFrames(videoId, modelId) {
  if (!videoId || !modelId) {
    throw new Error("Both videoId and modelId are required.");
  }

  try {
    // Fetch initial processing data
    const data = await fetchProcessing(videoId, modelId);

    if (!data) {
      console.error("No data returned from fetchProcessing.");
      return [];
    }

    const connectionId = data.connection_id || null;

    // If connectionId exists, switch to live updates
    if (connectionId) {
      console.log("Live connection detected. Starting socket updates...");
      setupLiveSocket(connectionId);
      return []; // Don't return static frames yet, live mode will handle updates
    }

    // Static mode: process returned frames
    if (!Array.isArray(data.frames)) {
      console.error("Invalid data format: 'frames' key missing or not an array.");
      return [];
    }

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
      return new Frame(frameData.frame_num, objects);
    });

    console.log("Processed frames:", frameObjects);
    return frameObjects;

  } catch (error) {
    console.error("Error fetching frames:", error);
    return [];
  }
}

// ---- Socket Handling ----
  function setupLiveSocket(connectionId) {
  if (socket) {
    socket.disconnect();
  }

  // Connect to backend Socket.IO
  socket = io.connect("/", {
    transports: ["websocket"], // Force WebSocket for reliability
  });

  socket.on("connect", () => {
    console.log("Connected to live socket server.");

    // Join the task-specific room
    socket.emit("join", connectionId);
    console.log(`Joined room: ${connectionId}`);
  });

  // Listen for incoming frames on the default 'message' event
  socket.on("message", (data) => {
    try {
      const frameData = JSON.parse(data);
      console.log("Live frame received:", frameData);

      const newObjects = frameData.objects.map(obj => new DetectionObject(
        obj.type, obj.x1, obj.x2, obj.y1, obj.y2, obj.confidence
      ));

      const newFrame = new Frame(frameData.frame_num, newObjects);
      frames.push(newFrame);

      // Update object dropdown dynamically
      newObjects.forEach(obj => {
        if (!liveObjectTypes.has(obj.object_type)) {
          liveObjectTypes.add(obj.object_type);

          const option = document.createElement("option");
          option.value = obj.object_type;
          option.textContent = obj.object_type;
          document.getElementById("objectTypeDropdown").appendChild(option);

          // Set the first type automatically if none selected
          if (!currentObjectType) {
            currentObjectType = obj.object_type;
            document.getElementById("objectTypeDropdown").value = currentObjectType;
          }
        }
      });

      // Update the graph live for the selected object type
      if (currentObjectType) {
        updateGraph(frames, currentObjectType);
      }
    } catch (err) {
      console.error("Error parsing incoming frame data:", err);
    }
  });

  socket.on("disconnect", () => {
    console.log("Socket disconnected from live server.");
  });
}

function updateGraph(frameList, objectType) {
    const filteredData = [];
    frameList.forEach(frame => {
      frame.objects.forEach(obj => {
        if (obj.object_type === objectType) {
          filteredData.push({ x: frame.frame_num, y: obj.confidence });
        }
      });
    });
    
    console.log("Updating graph with data:", filteredData);
    tempScatterChart.data.datasets[0].data = filteredData;
    tempScatterChart.data.datasets[0].label = `${objectType} Confidence per Frame`;
    tempScatterChart.update();
  }

  // Fetch and plot frames
  async function addDataPoints() {
    const videoId = document.getElementById("videoDropdown").value;
    const modelId = document.getElementById("modelDropdown").value;

    if (!videoId || !modelId) {
      alert("Please select both a video and a model.");
      return;
    }

    frames = await getFrames(videoId, modelId);

    if (frames.length === 0) {
      console.warn("No static frames returned or live mode started.");
      return;
    }

    // Find first available object type
    const firstFrameWithObjects = frames.find(frame => frame.objects.length > 0);
    if (!firstFrameWithObjects) {
      alert("No objects found in any frame.");
      return;
    }

    currentObjectType = firstFrameWithObjects.objects[0].object_type;
    updateGraph(frames, currentObjectType);
    populateDropdown(typeDropdown, frames);
  }

  const typeDropdown = document.getElementById("objectTypeDropdown");

  function populateDropdown(dropdown, frameList) {
    dropdown.innerHTML = ""; // Clear old options
    const typeSet = new Set();
    frameList.forEach(frame => {
      frame.objects.forEach(obj => typeSet.add(obj.object_type));
    });
    typeSet.forEach(type => {
      const option = document.createElement("option");
      option.value = type;
      option.textContent = type;
      dropdown.appendChild(option);
    });
    dropdown.value = currentObjectType;
  }

  typeDropdown.addEventListener("change", (e) => {
    currentObjectType = e.target.value;
    updateGraph(frames, currentObjectType);
  });

  document.getElementById("addDataBtn").addEventListener("click", addDataPoints);

  function findFrameFromPoint(frameNum) {
    const frame = frames.find(f => f.frame_num === frameNum);
    console.log("Frame clicked:", frame);
  }

document.addEventListener("DOMContentLoaded", () => {
  const ctx = document.getElementById("tempScatterChart").getContext("2d");

  const tempData = [];

  tempScatterChart = new Chart(ctx, {
    type: "scatter",
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
          title: { display: true, text: "Frames" }
        },
        y: {
          title: { display: true, text: "Confidence" },
          min: 0,
          max: 1
        }
      },
      plugins: {
        zoom: {
          limits: { x: { min: 0 }, y: { min: 0, max: 1 } },
          zoom: {
            drag: { enabled: true },
            mode: 'xy',
          }
        }
      },
      onClick: (event) => {
        const points = tempScatterChart.getElementsAtEventForMode(
          event,
          "nearest",
          { intersect: true },
          false
        );
        if (points.length) {
          const firstPoint = points[0];
          const value = tempScatterChart.data.datasets[0].data[firstPoint.index];
          console.log("Clicked point:", value);
          findFrameFromPoint(value.x);
        }
      }
    }
  });

  document.getElementById('resetZoom').addEventListener('click', () => {
    tempScatterChart.resetZoom();
  });

});
