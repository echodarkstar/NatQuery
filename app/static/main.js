$(document).ready(function () {
  console.log("ready!");
  // hidden();
});
function speak() {
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
}




var search_query = $("#speech_box").val();
console.log(search_query);

function search() {
  $.getJSON($SCRIPT_ROOT + '/query',{
    nat_query : $("#speech_box").val()
  }, function (data) {
    json_data = JSON.parse(data)
    console.log(json_data["sql_query"])
    var search_query = json_data["nl_query"];
    var main_query = json_data["sql_query"];
    var interpreted_words = json_data["interpreted"];
    var output = json_data["output"];
    // console.log(json_data["output"])
    var related_queries =json_data["related_queries"];
    // console.log(related_queries);
    // console.log(main_query,interpreted_words,output,related_queries);
    // console.log(data);
    // document.getElementById("speech_box").value = main_query;
    $("#main").empty();
    $("#side").remove();
    // console.log(value);
    //creating related queries div outside the main
    document.getElementById("main").setAttribute("class", "col-md-6");
    var input_box = document.createElement("div");
    input_box.setAttribute("class","panel panel-info");
    var input_box_head = document.createElement("div");
    input_box_head.setAttribute("class","panel-heading");
    input_box_head.innerHTML = "Query";
    var input_box_body = document.createElement("div");
    input_box_body.setAttribute("class","panel-body");
    var input_box_body_div = document.createElement("div");
    input_box_body_div.setAttribute("class","input-group btn-group");
    input_box_body_div.setAttribute("role","group");
    var input_box_body_input = document.createElement("input");
    input_box_body_input.setAttribute("type","text");
    input_box_body_input.setAttribute("class","form-control");
    input_box_body_input.setAttribute("id","speech_box");
    input_box_body_input.setAttribute("placeholder","Type your query...");
    input_box_body_input.setAttribute("value",search_query);
    var input_box_body_span = document.createElement("span");
    input_box_body_span.setAttribute("class","input-group-btn");
    var input_box_body_input_button1 = document.createElement("button");
    input_box_body_input_button1.setAttribute("type","button");
    input_box_body_input_button1.setAttribute("id","voice");
    input_box_body_input_button1.setAttribute("class","btn btn-default");
    input_box_body_input_button1.setAttribute("onclick","speak()");
    var voice_img = document.createElement("img");
    voice_img.setAttribute("src","static/voice.png");
    voice_img.setAttribute("id","voice_img");


    var input_box_body_input_button2 = document.createElement("button");
    input_box_body_input_button2.setAttribute("type","button");
    input_box_body_input_button2.setAttribute("id","search");
    input_box_body_input_button2.setAttribute("class","btn btn-default");
    input_box_body_input_button2.setAttribute("onclick","search()");

    var search_img = document.createElement("img");
    search_img.setAttribute("src","static/search.png");
    search_img.setAttribute("id","search_img");
    input_box_body_input_button2.appendChild(search_img);
    input_box_body_input_button1.appendChild(voice_img);
    input_box_body_span.appendChild(input_box_body_input_button1);
    input_box_body_span.appendChild(input_box_body_input_button2);
    // input_box_body_input.appendChild(input_box_body_span);
    input_box_body_div.appendChild(input_box_body_input);
    input_box_body_div.appendChild(input_box_body_span);
    input_box_body.appendChild(input_box_body_div);

    input_box.appendChild(input_box_head);
    input_box.appendChild(input_box_body);
    document.getElementById("main").appendChild(input_box);





    var related_box = document.createElement("div");
    related_box.setAttribute("class", "col-md-3");
    related_box.setAttribute("id","side");
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
    output_div_body.setAttribute("id","output_div");
    // output_div_body.innerHTML = output;
    var header = output[0];
    var keys2 = [];
    for(var k in header) keys2.push(k);
    // console.log(keys2);
    var output_div_table = document.createElement("table");
    output_div_table.setAttribute("id","table");
    output_div_table.setAttribute("class","table table-striped table-bordered");
    output_div_table.setAttribute("style","width:100%");
    output_div_body.appendChild(output_div_table);
    // output_div_table.setAttribute("id","output_div");
    // console.log("Len ", output[0]["actor.actor_id"]);
    var thead = document.createElement("thead");
    var tr_h = document.createElement("tr");
    thead.appendChild(tr_h)

    for(var i in keys2) {
      var th = document.createElement("th");
      th.innerHTML = keys2[i];
      tr_h.appendChild(th);
    }
    
    thead.appendChild(tr_h)
    output_div_table.appendChild(thead);

    var tbody = document.createElement("tbody");
    
    for (var i in output) {
      var tr1 = document.createElement("tr");
      for(var k in keys2) {
        var td1 = document.createElement("td");        
        // console.log(keys2[k])
        td1.innerHTML = output[i][keys2[k]];
        tr1.appendChild(td1);
      }
        tbody.appendChild(tr1)    
        
    }
    output_div_table.appendChild(tbody);
    $('#table').DataTable();
    

    output_div.appendChild(output_div_head);
    output_div.appendChild(output_div_body);
    document.getElementById("main").appendChild(output_div);

    //Suggestions div
    var suggestion_div = document.createElement("div");
    suggestion_div.setAttribute("class","panel panel-info");
    var suggestion_div_head = document.createElement("div");
    suggestion_div_head.setAttribute("class","panel-heading");
    suggestion_div_head.innerHTML = "Suggestions";
    var suggestion_div_body = document.createElement("div");
    suggestion_div_body.setAttribute("class","panel-body");
    suggestion_div_body.innerHTML = "...";
    suggestion_div.appendChild(suggestion_div_head);
    suggestion_div.appendChild(suggestion_div_body);
    related_box.appendChild(suggestion_div);

  })
}

// console.log(document.getElementById("speech_box").clientHeight);
// console.log(document.getElementById("voice").clientHeight);

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



