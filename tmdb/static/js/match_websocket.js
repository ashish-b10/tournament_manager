tmdb_vars = {};
tmdb_vars.tournament_data = {};

function store_initial_data(msg_json) {
  var msg_data = JSON.parse(msg_json);
  var tournament_data = tmdb_vars.tournament_data.tournament_slug;
  msg_data.map(function(d) {
    if (d.model == "tmdb.tournament") {
      tournament_data[d.model] = d;
      return;
    }
    if (tournament_data[d.model] == undefined) {
      tournament_data[d.model] = {};
    }
    tournament_data[d.model][d.pk] = d;
  });
}

function render_initial_display() {
  alert(JSON.stringify(tmdb_vars));
}

function handle_message(msg) {
  console.log(msg);
}

function on_websocket_open() {
  tmdb_vars.tournament_data.tournament_slug = {}

  var init_data_req = new XMLHttpRequest();
  init_data_req.onreadystatechange = function() {
    if (init_data_req.readyState == 4 && init_data_req.status == 200) {
      store_initial_data(init_data_req.responseText);
      render_initial_display();
      return;
    }
    if (init_data_req.readyState == 4) {
      var err_msg = "Error loading page: HTTP status code ";
      err_msg += init_data_req.status;
      err_msg += "\n\nresponse: ";
      err_msg += init_data_req.responseText;
      alert(err_msg);
    }
  }
  init_data_req.open("GET", tmdb_vars.initial_tournament_data_url, true);
  init_data_req.send(null);
}

function on_websocket_close() {
  setInterval(function() {
    alert("Lost connection to " + ws_url + "\n\nPlease reload the page.");
  }, 3500);
}

function start_teammatch_websocket(tournament_slug, tournament_json_url) {
  if (tmdb_vars.match_update_ws != null) {
    return;
  }
  var ws_url = "ws://" + window.location.host + "/tmdb/tournament/" + tournament_slug + "/match_updates/";
  tmdb_vars.initial_tournament_data_url = window.location.protocol + "//" + window.location.host + tournament_json_url;
  console.log("Opening connection to " + ws_url);
  tmdb_vars.match_update_ws = new WebSocket(ws_url);
  tmdb_vars.match_update_ws.onmessage = handle_message;
  tmdb_vars.match_update_ws.onopen = on_websocket_open;
  tmdb_vars.match_update_ws.onclose = on_websocket_close;
}
