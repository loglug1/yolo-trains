document.addEventListener("DOMContentLoaded", () => {
  const ctx = document.getElementById("tempScatterChart").getContext("2d");

  // Example temperature data (x = time, y = temperature)
  const tempData = [
    { x: 0, y: 22 },
    { x: 1, y: 24 },
    { x: 2, y: 23 },
    { x: 3, y: 25 },
    { x: 4, y: 26 },
    { x: 5, y: 28 }
  ];

  const tempScatterChart = new Chart(ctx, {
    type: "scatter",
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
});
