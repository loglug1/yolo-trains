import { Video, Model, Frame, DetectionObject } from './Classes.js';
import { fetchProcessing } from './api.js';
import { updateDataPane } from './dataPaneHandler.js';

var frames = [];
var liveObjectTypes = new Set(); // To track unique object types in live mode
var currentObjectType = null;    // Currently selected object type
var socket = null;               // Socket connection
var tempScatterChart = null;

export let frameClicked;

async function getFrames(videoId, modelId) {
  if (!videoId || !modelId) throw new Error("Both videoId and modelId are required.");

  try {
    const data = await fetchProcessing(videoId, modelId);

    if (!data) {
      console.error("No data returned from fetchProcessing.");
      return [];
    }

    const { connection_id: connectionId, frames: processedFrames = [] } = data;

    //Display any already processed frames
    let frameObjects = [];
    if (Array.isArray(processedFrames) && processedFrames.length > 0) {
      frameObjects = processedFrames.map(frameData => {
        const objects = frameData.objects.map(obj =>
          new DetectionObject(obj.type, obj.x1, obj.x2, obj.y1, obj.y2, obj.confidence)
        );
        return new Frame(frameData.frame_num, objects);
      });
      console.log("Loaded processed frames:", frameObjects);
    }

    //If connectionId exists, start live updates
    if (connectionId) {
      console.log("Live connection detected. Starting socket updates...");
      setupLiveSocket(connectionId);
    }

    return frameObjects;

  } catch (error) {
    console.error("Error fetching frames:", error);
    return [];
  }
}


// ---- Socket Handling ----
function setupLiveSocket(connectionId) {
  if (!connectionId) {
    console.warn("No connection ID provided for live socket.");
    return;
  }

  if (socket && socket.connected && socket.currentRoom) {
    console.log("Leaving previous room...");
    socket.emit("leave", socket.currentRoom);
    socket.off("processed_frame");
    socket.off("message");
    socket.off("disconnect");
  }

  // Connect to backend Socket.IO
  if (!socket) {
    socket = io.connect("/", {
      transports: ["websocket"],
    });
  }
  
  socket.currentRoom = connectionId;

  if (socket.connected) {
    console.log(`Already connected. Joining new room: ${connectionId}`);
    socket.emit("join", connectionId);
  }

  socket.on("connect", () => {
    console.log("Connected to live socket server.");

    // Join the task-specific room
    socket.emit("join", connectionId);
    console.log(`Joining room: ${connectionId}...`);
  });

  // Listen for general messages from the server
  socket.on("message", (data) => {
    console.log(`Message from the server: ${data}`);
  });

  // Listen for incoming frames on the 'processed_frame' event
  socket.on("processed_frame", (data) => {
    try {
      const frameData = JSON.parse(data);
      console.log("Live frame received:", frameData);

      const newObjects = frameData.objects.map(obj => new DetectionObject(
        obj.type, obj.x1, obj.x2, obj.y1, obj.y2, obj.confidence
      ));

      const newFrame = new Frame(frameData.frame_num, newObjects);
      frames.push(newFrame);

      const liveImageCheckbox = document.getElementById("liveImageCheckbox");
      if (liveImageCheckbox && liveImageCheckbox.checked) {
        const imgElement = document.getElementById("frame");
        if (imgElement) {
          imgElement.src = frameData.image; // base64 image directly
        }
      }

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
  const minthreshold = parseFloat(document.getElementById('minthresholdinput').value) || 0;
  const maxthreshold = parseFloat(document.getElementById('maxthresholdinput').value) || 0;

  const frameInterval = parseInt(document.getElementById('frameIntervalInput').value) || 1;
  const filteredData = [];

  frameList.forEach(frame => {
    // Apply both filters: confidence + every Nth frame
    if (frame.frame_num % frameInterval !== 0) return;

    frame.objects.forEach(obj => {
      if (obj.object_type === objectType && (obj.confidence >= minthreshold) && obj.confidence <= maxthreshold) {
        filteredData.push({ x: frame.frame_num, y: obj.confidence });
      }
    });
  });

  tempScatterChart.data.datasets[0].data = filteredData;
  tempScatterChart.data.datasets[0].label = `${objectType} Confidence per Frame`;
  tempScatterChart.update();
}

// Attach listener for live threshold updates
const minthresholdInput = document.getElementById('minthresholdinput');
minthresholdInput.addEventListener('input', () => {
  // Make sure frameList and objectType are accessible here (you may have them as globals or from current context)
  updateGraph(frames, currentObjectType);
});

const maxthresholdInput = document.getElementById('maxthresholdinput');
maxthresholdInput.addEventListener('input', () => {
  // Make sure frameList and objectType are accessible here (you may have them as globals or from current context)
  updateGraph(frames, currentObjectType);
});

const frameIntervalInput = document.getElementById('frameIntervalInput');
frameIntervalInput.addEventListener('input', () => {
  updateGraph(frames, currentObjectType);
});


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
    console.log(`frames for line 160: ${frames}`)
    const firstFrameWithObjects = frames.find(frame => frame.objects.length > 0);
    if (!firstFrameWithObjects) {
      alert("No objects found in any frame.");
      return;
    }

    currentObjectType = firstFrameWithObjects.objects[0].object_type;
    console.log(`frames: ${frames}`)
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

  //=====Gets frame from point clicked========================
  function findFrameFromPoint(frameNum) {
    const videoId = document.getElementById("videoDropdown").value;
    const modelId = document.getElementById("modelDropdown").value;
    const frame = frames.find(f => f.frame_num === frameNum);
    console.log("Frame clicked:", frame);
    frameClicked = frame;
    updateDataPane(modelId,videoId,frame)
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
          limits: { x: { min: 0}, y: { min: 0, max: frames.length + 1 } },
          zoom: {
            wheel: { enabled: true },
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
          console.log(frames.length)
        }
      }
    }
  });

  //Will reset the zoom of the graph
  document.getElementById('resetZoom').addEventListener('click', () => {
    tempScatterChart.resetZoom();
  });

});
