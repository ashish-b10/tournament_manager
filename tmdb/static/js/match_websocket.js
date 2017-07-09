tmdb_vars = {};
tmdb_vars.tournament_data = {};

function start_teammatch_websocket(tournament_slug) {
  if (tmdb_vars.match_update_ws == null) {
    var ws_url = "ws://" + window.location.host + "/tmdb/tournament/" + tournament_slug + "/match_updates/";
    tmdb_vars.match_update_ws = new WebSocket(ws_url);
    tmdb_vars.match_update_ws.onmessage = function(msg) {
      console.log(msg);
      var msg_data = JSON.parse(msg.data);
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
    tmdb_vars.match_update_ws.onopen = function() {
      console.log("Opened connection to " + ws_url);
      tmdb_vars.tournament_data.tournament_slug = {}
    }
    tmdb_vars.match_update_ws.onclose = function() {
      setInterval(function() {
        alert("Lost connection to " + ws_url + "\n\nPlease reload the page.");
      }, 3500);
    }
  }
}
