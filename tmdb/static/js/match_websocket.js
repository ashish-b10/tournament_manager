tmdb_vars = {};

function start_teammatch_websocket(tournament_slug) {
  if (tmdb_vars.match_update_ws == null) {
    var ws_url = "ws://" + window.location.host + "/tmdb/tournament/" + tournament_slug + "/match_updates/";
    tmdb_vars.match_update_ws = new WebSocket(ws_url);
    tmdb_vars.match_update_ws.onmessage = function(msg) {
      console.log(msg);
    }
    tmdb_vars.match_update_ws.onopen = function() {
      console.log("Opened connection to " + ws_url);
    }
    tmdb_vars.match_update_ws.onclose = function() {
      setInterval(function() {
        alert("Lost connection to " + ws_url + "\n\nPlease reload the page.");
      }, 3500);
    }
  }
}
