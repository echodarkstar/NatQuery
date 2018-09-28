$(document).ready(function () {
  console.log("ready!");
  // hidden();
});

var main_query, related_queries, output, interpreted_words;
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

function send_query(){
  $.getJSON($SCRIPT_ROOT + '/query',{
    nat_query : $("#speech_box").val()
  },function(data){
    console.log("Data: " + data);
  });
  return false;
}
  
//   console.log(query_data)
//   $.post( "/query", {
//     nat_query: query_data
//   },
//   function(data){
    
//   });
// })
  





function search() {
  $.getJSON("static/example.json", function (data) {
    var main_query = data["main_query"]["ques"];
    var interpreted_words = data["main_query"]["interpreted_words"];
    var output = data["main_query"]["output"];
    var related_queries = data["Related_queries"];
    // console.log(main_query,interpreted_words,output,related_queries);
    // console.log(data);
    // document.getElementById("speech_box").value = main_query;

    //creating related queries div outside the main
    document.getElementById("main").setAttribute("class", "col-md-6");
    var related_box = document.createElement("div");
    related_box.setAttribute("class", "col-md-4");
    document.getElementById("container").appendChild(related_box);

    //populating div with JSON

    var related_div = document.createElement("div");
    related_div.setAttribute("class", "panel panel-info");
    // related_div.setAttribute("class","panel-info");
    var related_div_head = document.createElement("div");
    related_div_head.setAttribute("class", "panel-heading");
    related_div_head.innerHTML = "Related Queries";
    var related_div_body = document.createElement("div");
    related_div_body.setAttribute("class", "panel-body");

    //iterating over related queries JSON
    var arr = ["0", "1", "2"]
    arr.forEach(function (value) {
      var related_div_body_parts = document.createElement("div");
      related_div_body_parts.setAttribute("class", " panel panel-info panel-body");
      related_div_body_parts.setAttribute("id", "ques" + value);
      var inner_text = document.createElement("div");
      inner_text.setAttribute("id", "text" + value);
      inner_text.setAttribute("data-y", parseInt(value));
      inner_text.innerText = related_queries[value];
      related_div_body_parts.appendChild(inner_text);
      // related_div_body_parts.innerHTML = related_queries[value];
      related_div_body_parts.setAttribute("onclick", "animated(this.id)");
      related_div_body.appendChild(related_div_body_parts);
      // document.getElementById("related_box").appendChild(related_div);
    });
    related_div.appendChild(related_div_head);
    related_div.appendChild(related_div_body);
    related_box.appendChild(related_div);

    //Interpreted words div

    var interpreted_div = document.createElement("div");
    interpreted_div.setAttribute("class", "panel panel-info");
    // interpreted_div.setAttribute("class","panel-info");
    var interpreted_div_head = document.createElement("div");
    interpreted_div_head.setAttribute("class", "panel-heading");
    interpreted_div_head.innerHTML = "Interpreted words";
    var interpreted_div_body = document.createElement("div");
    interpreted_div_body.setAttribute("class", "panel-body");
    interpreted_div_body.innerHTML = interpreted_words;
    interpreted_div.appendChild(interpreted_div_head);
    interpreted_div.appendChild(interpreted_div_body);
    document.getElementById("main").appendChild(interpreted_div);

    //SQL query

    var query_div = document.createElement("div");
    query_div.setAttribute("class", "panel panel-info");
    // interpreted_div.setAttribute("class","panel-info");
    var query_div_head = document.createElement("div");
    query_div_head.setAttribute("class", "panel-heading");
    query_div_head.innerHTML = "SQL query";
    var query_div_body = document.createElement("div");
    query_div_body.setAttribute("class", "panel-body");
    query_div_body.innerHTML = main_query;
    query_div.appendChild(query_div_head);
    query_div.appendChild(query_div_body);
    document.getElementById("main").appendChild(query_div);

    //Output div

    var output_div = document.createElement("div");
    output_div.setAttribute("class", "panel panel-info");
    // output_div.setAttribute("class","panel-info");
    var output_div_head = document.createElement("div");
    output_div_head.setAttribute("class", "panel-heading");
    output_div_head.innerHTML = "Output";
    var output_div_body = document.createElement("div");
    output_div_body.setAttribute("class", "panel-body");
    output_div_body.innerHTML = output;
    output_div.appendChild(output_div_head);
    output_div.appendChild(output_div_body);
    document.getElementById("main").appendChild(output_div);
  })
}

console.log(document.getElementById("speech_box").clientHeight);
console.log(document.getElementById("voice").clientHeight);

//Animation functions

function animated(click_id) {
  // console.log(click_id[4]);
  var animate = anime({
    targets: '#text' + click_id[4],
    translateX: [{
      value: '-41em',
      duration: 1200
    }],
    translateY: function (target) {
      return -10 - 51 * target.getAttribute("data-y");
    },
    easing: 'easeOutQuart',
    complete: function (anim) {
      console.log("completed", anim.completed);
      animated2(click_id);

    }
  });

}

function animated2(click_id) {
  // console.log("#text"+click_id[4]);
  // console.log(document.getElementById("#text"+click_id[4]));
  document.getElementById("speech_box").value = document.getElementById("text" + click_id[4]).innerHTML;
  document.getElementById("text" + click_id[4]).style.display = "none";
  // console.log("done");
}

function render_db(){
  $.getJSON("static/pagila_db.json",function(data){
    // console.log(data);
    var keys = Object.keys(data);
    for( var i in keys) {
      // var db_panel = document.createElement("div");
      // db_panel.setAttribute("class","panel panel-default");
      var db_panel_body = document.createElement("div");
      db_panel_body.setAttribute("class","panel-body");
      db_panel_body.setAttribute("id",keys[i]);
      db_panel_body.innerHTML = keys[i];
      // db_panel_body.setAttribute("onload","hidden(this.id)");
      db_panel_body.setAttribute("onclick","toggled(this.id)");
      var db_panel_footer = document.createElement("div");
      db_panel_footer.setAttribute("class","panel-footer");
      db_panel_footer.setAttribute("id","columns_"+keys[i]);
      db_panel_footer.setAttribute("style","display:none");
      var image = document.createElement("img");
      image.setAttribute("src","static/arrow.png");
      // image.setAttribute("style","float:right");
      image.setAttribute("height","8em");
      image.setAttribute("id","img_"+keys[i]);
      // image.setAttribute("onclick","rotated(this.id)");
      for(var j in data[keys[i]]){
        var list =  data[keys[i]][j] + "<br>";
        db_panel_footer.innerHTML += list;
      }
      db_panel_body.appendChild(image);
      db_panel_body.appendChild(db_panel_footer);
      // db_panel.appendChild(db_panel_body);
      // db_panel_body_container.appendChild(db_panel_body);
      document.getElementById("db_container").appendChild(db_panel_body);
      // console.log(data[keys[i]]);
    }
  })
}
render_db();

function toggled(clicked_id) {
  var id = "#columns_" + clicked_id;
  $(id).animate({
    height : 'toggle'
  })
}
