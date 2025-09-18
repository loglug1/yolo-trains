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

            return new Frame(frameData.frame_num, objects);
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
      ,plugins: {
        zoom: {
          limits: {
              x: {min: 0},
              y: {min: 0, max: 1}
          },
          zoom: {
            drag: {
              enabled: true,
            },
            mode: 'xy',
          }
        }
      },
      onClick: (event,elements,chart) => {
        const points = tempScatterChart.getElementsAtEventForMode(
          event,
          "nearest", // could also use "point"
          { intersect: true }, // only fire if directly on a point
          false
        );

          if (points.length) {
            const firstPoint = points[0];
            const datasetIndex = firstPoint.datasetIndex;
            const index = firstPoint.index;
            const value = tempScatterChart.data.datasets[datasetIndex].data[index];

            console.log("Clicked point:", value); // {x: frame, y: confidence}

            // Example: store or use the values
            const frameCliked = value.x;
            const confidenceClicked = value.y;
        }
      }
    }
  });

    document.getElementById('resetZoom').addEventListener('click', () => {
      tempScatterChart.resetZoom();
    });

  
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

    // Fetch and process frames
    const frames = await getFrames(videoId, modelId);

    if (frames.length === 0) {
      alert("No frames were returned from the server.");
      return;
    }

    console.log("Frames retrieved:", frames);

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

