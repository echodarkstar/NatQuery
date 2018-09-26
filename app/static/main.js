$(document).ready(function () {
  console.log("ready!");
});

var main_query,related_queries,output,interpreted_words;
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

function search() {
  $.getJSON("static/example.json",function(data){
    var main_query = data["main_query"]["ques"];
    var interpreted_words = data["main_query"]["interpreted_words"];
    var output = data["main_query"]["output"];
    var related_queries = data["Related_queries"];
    // console.log(main_query,interpreted_words,output,related_queries);
    // console.log(data);
    // document.getElementById("speech_box").value = main_query;

    //creating related queries div outside the main
    document.getElementById("main").setAttribute("class","col-md-6");
    var related_box = document.createElement("div");
    related_box.setAttribute("class","col-md-4");
    document.getElementById("container").appendChild(related_box);

    //populating div with JSON

    var related_div = document.createElement("div");
    related_div.setAttribute("class","panel panel-info");
    // related_div.setAttribute("class","panel-info");
    var related_div_head = document.createElement("div");
    related_div_head.setAttribute("class","panel-heading");
    related_div_head.innerHTML = "Related Queries";
    var related_div_body = document.createElement("div");
    related_div_body.setAttribute("class","panel-body");
    
    //iterating over related queries JSON
    var arr = ["0","1","2"]
    arr.forEach(function(value){
      var related_div_body_parts = document.createElement("div");
      related_div_body_parts.setAttribute("class"," panel panel-info panel-body");
      related_div_body_parts.setAttribute("id","ques"+value);
      related_div_body_parts.innerHTML = related_queries[value];
      related_div_body.appendChild(related_div_body_parts);
      // document.getElementById("related_box").appendChild(related_div);
    }); 
    related_div.appendChild(related_div_head);
    related_div.appendChild(related_div_body);
    related_box.appendChild(related_div);
    
    //Interpreted words div

    var interpreted_div = document.createElement("div");
    interpreted_div.setAttribute("class","panel panel-info");
    // interpreted_div.setAttribute("class","panel-info");
    var interpreted_div_head = document.createElement("div");
    interpreted_div_head.setAttribute("class","panel-heading");
    interpreted_div_head.innerHTML = "Interpreted words";
    var interpreted_div_body = document.createElement("div");
    interpreted_div_body.setAttribute("class","panel-body");
    interpreted_div_body.innerHTML = interpreted_words;
    interpreted_div.appendChild(interpreted_div_head);
    interpreted_div.appendChild(interpreted_div_body);
    document.getElementById("main").appendChild(interpreted_div);

    //SQL query

    var query_div = document.createElement("div");
    query_div.setAttribute("class","panel panel-info");
    // interpreted_div.setAttribute("class","panel-info");
    var query_div_head = document.createElement("div");
    query_div_head.setAttribute("class","panel-heading");
    query_div_head.innerHTML = "SQL query";
    var query_div_body = document.createElement("div");
    query_div_body.setAttribute("class","panel-body");
    query_div_body.innerHTML = main_query;
    query_div.appendChild(query_div_head);
    query_div.appendChild(query_div_body);
    document.getElementById("main").appendChild(query_div);

    //Output div

    var output_div = document.createElement("div");
    output_div.setAttribute("class","panel panel-info");
    // output_div.setAttribute("class","panel-info");
    var output_div_head = document.createElement("div");
    output_div_head.setAttribute("class","panel-heading");
    output_div_head.innerHTML = "Output";
    var output_div_body = document.createElement("div");
    output_div_body.setAttribute("class","panel-body");
    output_div_body.innerHTML = output;
    output_div.appendChild(output_div_head);
    output_div.appendChild(output_div_body);
    document.getElementById("main").appendChild(output_div);
  })
}

//Animation functions

