tmdb_vars = {};
tmdb_vars.tournament_data = {};

function delete_tourament_datum(datum) {
  datum.model = datum.model.replace(".", "_");
  delete tmdb_vars.tournament_data[datum.model][datum.pk];
}

function store_tournament_datum(datum) {
  datum.model = datum.model.replace(".", "_");
  if (datum.model == "tmdb_tournament") {
    tmdb_vars.tournament_data[datum.model] = datum;
    return;
  }
  if (tmdb_vars.tournament_data[datum.model] == undefined) {
    tmdb_vars.tournament_data[datum.model] = {};
  }
  tmdb_vars.tournament_data[datum.model][datum.pk] = datum;
}

function store_initial_data(msg_json) {
  var msg_data = JSON.parse(msg_json);
  msg_data.map(store_tournament_datum);
}

function createTextElem(elem_type, elem_content) {
  var elem = document.createElement(elem_type);
  elem.innerHTML = elem_content;
  return elem;
}

function createObjectElem(elem_type, elem_content) {
  var elem = document.createElement(elem_type);
  elem.appendChild(elem_content);
  return elem;
}

function render_initial_display() {
  render_full_display();
}

function render_updated_display() {
  render_full_display();
}

function render_full_display() {
  var match_queues = document.getElementsByClassName("division-queue");
  for (var i = 0; i < match_queues.length; ++i) {
    match_queue = match_queues[i];
    match_queue.innerHTML = '';
    var match_queue_table = document.createElement("table");
    match_queue_table.className += "table table-striped match_table table";
    match_queue.appendChild(match_queue_table);
    var match_queue_table_header = document.createElement("thead");
    match_queue_table.appendChild(match_queue_table_header);
    var match_queue_row = document.createElement("tr");
    match_queue_table_header.appendChild(match_queue_row);
    match_queue_row.appendChild(createTextElem("th", "Match No."));
    match_queue_row.appendChild(createTextElem("th", "Round"));
    match_queue_row.appendChild(createTextElem("th", "Blue Team"));
    match_queue_row.appendChild(createTextElem("th", "Red Team"));
    match_queue_row.appendChild(createTextElem("th", "In Holding?"));
    match_queue_row.appendChild(createTextElem("th", "Ring No."));
    match_queue_row.appendChild(createTextElem("th", "Winning Team"));
    match_queue_row.appendChild(createTextElem("th", "Status"));
    match_queue_row.appendChild(createTextElem("th", "Match Sheet"));
    var team_matches = Object.values(
        tmdb_vars.tournament_data.tmdb_teammatch);
    team_matches = team_matches.sort(function(team_match1, team_match2) {
      return team_match1.fields.number - team_match2.fields.number;
    });
    var match_queue_table_body = document.createElement("tbody");
    match_queue_table.appendChild(match_queue_table_body);
    team_matches.map(function(team_match) {
      match_queue_row = document.createElement("tr");
      match_queue_table_body.appendChild(match_queue_row);
      match_queue_row.append(createTextElem("td", team_match.fields.number));
      match_queue_row.append(createTextElem("td", render_round_num(team_match)));
      match_queue_row.append(createTextElem("td", render_blue_team_name(team_match)));
      match_queue_row.append(createTextElem("td", render_red_team_name(team_match)));
      match_queue_row.append(createObjectElem("td", render_in_holding(team_match)));
      match_queue_row.append(createObjectElem("td", render_ring_number(team_match)));
      match_queue_row.append(createObjectElem("td", render_winning_team(team_match)));
      match_queue_row.append(createTextElem("td", render_status(team_match)));
      match_queue_row.append(createObjectElem("td", render_match_sheet(team_match)));
    });
  }
}

function render_round_num(team_match) {
  var round_num = parseInt(team_match.fields.round_num);
  if (round_num == 0)
    return "Finals";
  if (round_num == 1)
    return "Semi-Finals";
  if (round_num == 2)
    return "Quarter-Finals";
  return "Round of " + 2**round_num;
}

function render_blue_team_name(team_match) {
  return render_team_registration(team_match.fields.blue_team);
}

function render_red_team_name(team_match) {
  return render_team_registration(team_match.fields.red_team);
}

function render_team_registration(team_registration_id) {
  if (team_registration_id == null) {
    return null;
  }
  var team_registration = tmdb_vars.tournament_data.tmdb_teamregistration[team_registration_id];
  var team_id = team_registration.fields.team;
  var team = tmdb_vars.tournament_data.tmdb_team[team_id];
  var school_str = render_school_name(team.fields.school);
  var division_id = team.fields.division;
  var division_str = render_division_name(division_id);
  return school_str + " " + division_str + team.fields.number;
}

function render_division_name(division_id) {
  var division = tmdb_vars.tournament_data.tmdb_division[division_id];
  var division_sex_str = "Unknown";
  if (division.fields.sex == "F")
    division_sex_str = "Women's";
  if (division.fields.sex == "M")
    division_sex_str = "Men's";
  return division_sex_str + " " + division.fields.skill_level;
}

function render_school_name(school_id) {
  var school = tmdb_vars.tournament_data.tmdb_school[school_id];
  return school.fields.name;
}

function render_in_holding(team_match) {
  var check_box = document.createElement("input");
  check_box.type = "checkbox";
  check_box.name = "in_holding";
  check_box.value = team_match.pk;
  check_box.checked = team_match.fields.in_holding;
  check_box.onclick = function() {
    on_in_holding_changed(this, team_match.pk);
  };
  return check_box;
}

function render_ring_number(team_match) {
  var text_field = document.createElement("input");
  text_field.type = "number";
  text_field.name = "ring_number";
  text_field.value = team_match.fields.ring_number;
  text_field.onchange = function() {
    on_ring_number_changed(this, team_match.pk);
  }
  return text_field;
}

function render_winning_team(team_match) {
  var select_menu = document.createElement("select");
  var option = document.createElement("option");
  option.value = '';
  option.innerHTML = "---";
  select_menu.appendChild(option);
  if (team_match.fields.blue_team != null) {
    option = document.createElement("option");
    option.value = team_match.fields.blue_team;
    option.innerHTML = render_blue_team_name(team_match);
    select_menu.appendChild(option);
  }
  if (team_match.fields.red_team != null) {
    option = document.createElement("option");
    option.value = team_match.fields.red_team;
    option.innerHTML = render_red_team_name(team_match);
    select_menu.appendChild(option);
  }
  select_menu.onchange = function() {
    on_winning_team_changed(this, team_match.pk);
  }
  select_menu.value = team_match.fields.winning_team;
  return select_menu;
}

function render_status(team_match) {
  var match_status = evaluate_status(team_match);
  return match_status.match_status_text;
}

function render_match_sheet(team_match) {
  var hyperlink = document.createElement("a");
  hyperlink.className += "btn btn-primary";
  hyperlink.href = "/tmdb/match_sheet?team_match_pk=" + team_match.pk;
  hyperlink.innerHTML = "Print";
  return hyperlink;
}

function evaluate_status(team_match) {
  if (team_match.fields.winning_team != null) {
    return {
        match_status_code: 3,
        match_status_text: "Complete"
    };
  }
  if (team_match.fields.ring_number != null) {
    return {
        match_status_code: 2,
        match_status_text: "At ring " + team_match.fields.ring_number
    };
  }
  if (team_match.fields.in_holding) {
    return {
        match_status_code: 1,
        match_status_text: "Report to holding"
    };
  }
  return {
      match_status_code: 0,
      match_status_text: ""
  };
}

function handle_message(msg) {
  console.log(msg);
  var data = JSON.parse(msg.data);
  if ('update' in data) {
    var update_data = JSON.parse(data['update']);
    update_data.map(store_tournament_datum);
  }
  if ('delete' in data) {
    var delete_data = JSON.parse(data['delete']);
    delete_data.map(delete_tourament_datum);
  }
  if ('error' in data) {
    var error_data = JSON.parse(data['error']);
    alert(error_data);
    render_updated_display();
    return
  }
  render_updated_display();
}

function on_websocket_open() {
  tmdb_vars.tournament_data = {}

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
    alert("Lost connection to " + tmdb_vars.match_update_ws.url + "\n\nPlease reload the page.");
  }, 3500);
}

function start_teammatch_websocket(tournament_slug, tournament_json_url) {
  if (tmdb_vars.match_update_ws != null) {
    return;
  }
  var ws_url = "ws://" + window.location.host + "/tmdb/tournament/" + tournament_slug + "/match_updates/";
  tmdb_vars.tournament_data.tournament_slug = tournament_slug;
  tmdb_vars.initial_tournament_data_url = window.location.protocol + "//" + window.location.host + tournament_json_url;
  console.log("Opening connection to " + ws_url);
  tmdb_vars.match_update_ws = new WebSocket(ws_url);
  tmdb_vars.match_update_ws.onmessage = handle_message;
  tmdb_vars.match_update_ws.onopen = on_websocket_open;
  tmdb_vars.match_update_ws.onclose = on_websocket_close;
}

function on_in_holding_changed(element, team_match_pk) {
  var team_match = {};
  team_match.model = 'tmdb.teammatch';
  team_match.pk = team_match_pk;
  team_match.fields = {};
  team_match.fields.in_holding = element.checked;
  tmdb_vars.match_update_ws.send(JSON.stringify([team_match]));
}

function on_ring_number_changed(element, team_match_pk) {
  var team_match = {};
  team_match.model = 'tmdb.teammatch';
  team_match.pk = team_match_pk;
  team_match.fields = {};
  if (element.value) {
    team_match.fields.ring_number = element.value;
  } else {
    team_match.fields.ring_number = null;
  }
  tmdb_vars.match_update_ws.send(JSON.stringify([team_match]));
}

function on_winning_team_changed(element, team_match_pk) {
  var team_match = {};
  team_match.model = 'tmdb.teammatch';
  team_match.pk = team_match_pk;
  team_match.fields = {};
  team_match.fields.winning_team = element.value;
  if (team_match.fields.winning_team == "") {
    team_match.fields.winning_team = null;
  }
  tmdb_vars.match_update_ws.send(JSON.stringify([team_match]));
}
