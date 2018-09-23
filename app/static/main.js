$(document).ready(function () {
  console.log("ready!");
});

d3.json("static/example.hexjson", function (error, hexjson) {

  // Set the size and margins of the svg
  var w = window.innerWidth / 2 - 100;
  var h = window.innerHeight / 2;
  var margin = {
      top: 10,
      right: 10,
      bottom: 10,
      left: 10
    },
    width = w - margin.left - margin.right,
    height = h - margin.top - margin.bottom;

  // Create the svg element
  var svg = d3
    .select("#vis")
    .append("svg")
    .attr("width", width)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // Render the hexes
  var hexes = d3.renderHexJSON(hexjson, width, height);

  // Bind the hexes to g elements of the svg and position them
  var hexmap = svg
    .selectAll("g")
    .data(hexes)
    .enter()
    .append("g")
    .attr("transform", function (hex) {
      return "translate(" + hex.x + "," + hex.y + ")";
    });

  // Draw the polygons around each hex's centre
  hexmap
    .append("polygon")
    .attr("points", function (hex) {
      return hex.points;
    })
    .attr("stroke", "white")
    .attr("stroke-width", "2")
    .attr("fill", "#bff5fc");

  // Add the hex codes as labels
  hexmap
    .append("text")
    .append("tspan")
    .attr("text-anchor", "middle")
    .text(function (hex) {
      return hex.key;
    });
});

window.SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;

const recognition = new SpeechRecognition();
const icon = document.getElementById('voice')
const speech_box = document.getElementById('speech_box');

icon.addEventListener('click', () => {
  dictate();
});

const dictate = () => {
  recognition.start();
  recognition.onresult = (event) => {
    const speechToText = event.results[0][0].transcript;

    speech_box.value = speechToText;
    console.log(speech_box.textContent);
    speech_box.disabled = false;
  }
}