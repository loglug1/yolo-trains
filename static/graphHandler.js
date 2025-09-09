import {Video, Model, Frame, Object} from './Classes'

document.addEventListener("DOMContentLoaded", () => {
  const ctx = document.getElementById("tempScatterChart").getContext("2d");

  // Example temperature data (x = time, y = temperature)
  const tempData = [];

  const tempScatterChart = new Chart(ctx, {
    type: "line",
    data: {
      datasets: [
        {
          label: "Objects confidence per frame",
          data: tempData,
          pointBackgroundColor: "red",
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
          }
        }
      }
    }
  });

  // Example function to update chart dynamically
  window.addTempDataPoint = (time, temp) => {
    tempScatterChart.data.datasets[0].data.push({ x: time, y: temp });
    tempScatterChart.update();
  };

  let counter = 1;
  let intervalId;

  function addDataPoints(){
  intervalId = setInterval(() => {
    tempData.push({ x: counter, y: Math.floor(Math.random() * 10) + 20 });
    tempScatterChart.update();
    counter++;
    if (counter > 10000) {
      clearInterval(intervalId); // stop after 10 points
    }
  }, 1000); // run every 10 seconds
  }

  // Attach event listener to button
  document.getElementById("addDataBtn").addEventListener("click", addDataPoints);

});