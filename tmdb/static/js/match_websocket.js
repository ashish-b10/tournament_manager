tmdb_vars = {};
tmdb_vars.tournament_data = {};
tmdb_vars_REPORT_STATUS_EMPTY_VALUE = 0;
tmdb_vars_REPORT_STATUS_HOLDING_VALUE = 1;
tmdb_vars_REPORT_STATUS_AT_RING_VALUE = 2;
tmdb_vars_REPORT_STATUS_COMPETING_VALUE = 3;

tmdb_vars_MATCH_STATUS_CODE_SENT_NOT_STARTED = 4;
tmdb_vars_MATCH_STATUS_CODE_SENT_IN_HOLDING  = 5;
tmdb_vars_MATCH_STATUS_CODE_SENT_TO_RING  = 6;
tmdb_vars_MATCH_STATUS_CODE_AT_RING  = 7;
tmdb_vars_MATCH_STATUS_CODE_COMPLETE = 8;

tmdb_vars_MAX_NUM_RINGS = 9;

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
  // Hide the loader if the data has been loaded.
  document.getElementById("loader-wrapper").style = "display:none";
  render_full_display();
}

function render_updated_display() {
  render_full_display();
}

function set_show_all_filter() {
  tmdb_vars.team_match_filter = function(team_match) {
    return true;
  }
}

function set_active_matches_filter() {
  tmdb_vars.team_match_filter = function(team_match) {
    var match_status = evaluate_status(team_match);
     if (match_status['match_status_code'] == tmdb_vars_REPORT_STATUS_COMPETING_VALUE) {
        return true;
     }
    if (match_status['match_status_code'] == tmdb_vars_MATCH_STATUS_CODE_SENT_IN_HOLDING) {
      return true;
    }
    if (match_status['match_status_code'] == tmdb_vars_MATCH_STATUS_CODE_SENT_TO_RING) {
      return true;
    }
    if (match_status['match_status_code'] == tmdb_vars_MATCH_STATUS_CODE_AT_RING) {
      return true;
    }
    return false;
  }
}

function set_ring_number_filter() {
  var filter_value_div = document.getElementById('filter_value');
  var filter_value_type = document.createElement('input');
  filter_value_type.setAttribute('id', 'ring_number_filter');
  filter_value_type.setAttribute('type', 'number');
  $(filter_value_type).on('change', function(e) {
    var filter_ring_number = $(e.currentTarget).val();
    if (typeof parseInt(filter_ring_number) == 'number') {
      tmdb_vars.team_match_filter = function(team_match) {
        return team_match.fields.ring_number == filter_ring_number;
      }
    } else {
      set_show_all_filter();
    }
    render_full_display();
  });
  filter_value_div.appendChild(filter_value_type);
}

function set_division_filter() {
  var filter_value_div = document.getElementById('filter_value');
  var filter_value_type = document.createElement('select');
  filter_value_div.appendChild(filter_value_type);

  var division_objs = Object.values(tmdb_vars.tournament_data.tmdb_division);
  var division_names = division_objs.map(x => x.pk).map(render_division_name).sort();

  var option = document.createElement('option');
  option.value = '';
  option.text = '---';
  filter_value_type.appendChild(option);

  for (var division_num = 0; division_num < division_names.length; division_num++) {
    var option = document.createElement('option');
    option.value = division_names[division_num];
    option.text = division_names[division_num];
    filter_value_type.appendChild(option);
  }

  $(filter_value_type).on('change', function(e) {
    var selected_division = $(e.currentTarget).find(":selected").val();
    if (selected_division == '') {
      set_show_all_filter();
      render_full_display();
      return;
    }
    tmdb_vars.team_match_filter = function(team_match) {
      return get_division(team_match) == selected_division;
    }
    render_full_display();
  });
}

function set_school_filter() {
  var filter_value_div = document.getElementById('filter_value');
  var filter_value_type = document.createElement('select');
  filter_value_div.appendChild(filter_value_type);

  var school_reg_objs = Object.values(tmdb_vars.tournament_data.tmdb_schoolregistration);
  var school_ids = school_reg_objs.map(x => x.fields.school);
  var school_names = school_ids.map(render_school_name).sort();

  var option = document.createElement('option');
  option.value = '';
  option.text = '---';
  filter_value_type.appendChild(option);

  for (var school_num = 0; school_num < school_names.length; school_num++) {
    var option = document.createElement('option');
    option.value = school_names[school_num];
    option.text = school_names[school_num];
    filter_value_type.appendChild(option);
  }

  $(filter_value_type).on('change', function(e) {
    var selected_school = $(e.currentTarget).find(":selected").val();
    if (selected_school == '') {
      set_show_all_filter();
      render_full_display();
      return;
    }
    tmdb_vars.team_match_filter = function(team_match) {
      var blue_school_name = get_school_name_from_team_registration(
          team_match.fields.blue_team);
      if (blue_school_name == selected_school) {
        return true;
      }
      var red_school_name = get_school_name_from_team_registration(
          team_match.fields.red_team);
      if (red_school_name == selected_school) {
        return true;
      }
      return false;
    }
    render_full_display();
  });
}

function add_filter_options() {
  var filter_label = document.getElementById('filter-label');
  if (filter_label.innerHTML != "") {
    return;
  }
  filter_label.innerHTML = "Filter matches:"
  var filter_div = document.getElementById('filter_type');
  var filter_type_elem = document.createElement('select');
  filter_div.append(filter_type_elem);
  tmdb_vars.team_match_filters = {
    "show_all": set_show_all_filter,
    "active_matches": set_active_matches_filter,
    "by_ring": set_ring_number_filter,
    "by_division": set_division_filter,
    "by_school": set_school_filter,
  };
  var filter_order = [
    ["Show all", "show_all"],
    ["Active matches", "active_matches"],
    ["By ring", "by_ring"],
    ["By division", "by_division"],
    ["By school", "by_school"],
  ];
  for (var filter_num = 0; filter_num < filter_order.length; filter_num++) {
    var option = document.createElement("option");
    option.value = filter_order[filter_num][1];
    option.text = filter_order[filter_num][0];
    filter_type_elem.appendChild(option);
  }

  $('#filter_type').on('change', function(e) {
    var filter_value_div = document.getElementById('filter_value');
    filter_value_div.innerHTML = '';
    var selected_filter_val = $(e.currentTarget).find(":selected").val();
    var selected_filter = tmdb_vars.team_match_filters[selected_filter_val];
    selected_filter();
    render_full_display();
  });

  set_show_all_filter();
}

function render_full_display() {
  var match_queues = document.getElementsByClassName("division-queue");
  for (var i = 0; i < match_queues.length; ++i) {
    match_queue = match_queues[i];
    match_queue.innerHTML = '';

    if (tmdb_vars.tournament_data.tmdb_teammatch === undefined) {
      var empty_match_list = createTextElem("div", "No matches have been created for this tournament.");
      empty_match_list.className += "alert alert-warning";
      match_queue.appendChild(empty_match_list);
      continue;
    }
    var team_matches = Object.values(
        tmdb_vars.tournament_data.tmdb_teammatch);

    add_filter_options();
    var match_queue_table = document.createElement("table");
    match_queue_table.className += "table match_table table";
    match_queue.appendChild(match_queue_table);
    var match_queue_table_header = document.createElement("thead");
    match_queue_table.appendChild(match_queue_table_header);
    var match_queue_row = document.createElement("tr");
    match_queue_table_header.appendChild(match_queue_row);
    match_queue_row.appendChild(createTextElem("th", "Match No."));
    match_queue_row.appendChild(createTextElem("th", "Round"));
    match_queue_row.appendChild(createTextElem("th", "Blue Team"));
    match_queue_row.appendChild(createTextElem("th", "Red Team"));
    match_queue_row.appendChild(createTextElem("th", "Report Status"));
    match_queue_row.appendChild(createTextElem("th", "Ring No."));
    match_queue_row.appendChild(createTextElem("th", "Winning Team"));
    match_queue_row.appendChild(createTextElem("th", "Status"));
    team_matches = team_matches.sort(function(team_match1, team_match2) {
      return team_match1.fields.number - team_match2.fields.number;
    });
    var match_queue_table_body = document.createElement("tbody");
    match_queue_table.appendChild(match_queue_table_body);
    team_matches.filter(tmdb_vars.team_match_filter).map(function(team_match) {
      match_queue_row = document.createElement("tr");
      match_queue_table_body.appendChild(match_queue_row);
      match_queue_row.append(createTextElem("td", team_match.fields.number));
      match_queue_row.append(createTextElem("td", render_round_num(team_match)));
      match_queue_row.append(createTextElem("td", render_blue_team_name(team_match)));
      match_queue_row.append(createTextElem("td", render_red_team_name(team_match)));
      match_queue_row.append(createObjectElem("td", render_report_status(team_match)));
      match_queue_row.append(createObjectElem("td", render_ring_number(team_match)));
      match_queue_row.append(createObjectElem("td", render_winning_team(team_match)));
      match_queue_row.append(createTextElem("td", render_status(team_match)));
      var match_status = evaluate_status(team_match);
      match_queue_row.className = match_status['match_status_css_class'];
    });
  }
}

function get_division(match) {
  if (match == null) {
    return null;
  }
  var tournament_division = tmdb_vars.tournament_data.tmdb_tournamentdivision[match.fields.division];
  var division = tmdb_vars.tournament_data.tmdb_division[tournament_division.fields.division];
  var tournamentdivision_id = match.fields.division;
  var division_str = render_division_name(tournament_division.fields.division);
return division_str + "";
}

function render_round_num(team_match) {
  var round_num = parseInt(team_match.fields.round_num);
  if (round_num == 0)
    return "Finals";
  if (round_num == 1)
    return "Semi-Finals";
  if (round_num == 2)
    return "Quarter-Finals";
   // Added 1 because round numbers start at 0, not 1
  return "Round of " + 2**(round_num + 1);
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
  var team_composition = render_team_composition(team_registration)
  var team_display = school_str + " " + division_str + team.fields.number;
  if (team_composition) {
    team_display = team_display + " " + team_composition;
  }
  return team_display;
}

function render_team_composition(team_registration) {
    var lightweight = team_registration.fields.lightweight ? "L" :  ""
    var middleweight = team_registration.fields.middleweight ? "M" :  ""
    var heavyweight = team_registration.fields.heavyweight ? "H" :  ""
    if (!(lightweight || middleweight || heavyweight)) {
        return ""
    }
    return "(" + lightweight + middleweight + heavyweight + ")"
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

function render_report_status(team_match) {
  var select_menu = document.createElement("select");
  var empty_option = document.createElement("option");
  var holding_option = document.createElement("option");
  var at_ring_option = document.createElement("option");
  var competing_option = document.createElement("option");

  empty_option.value = tmdb_vars_REPORT_STATUS_EMPTY_VALUE;
  holding_option.value = tmdb_vars_REPORT_STATUS_HOLDING_VALUE;
  at_ring_option.value = tmdb_vars_REPORT_STATUS_AT_RING_VALUE;
  competing_option.value = tmdb_vars_REPORT_STATUS_COMPETING_VALUE;

  empty_option.innerHTML = "---";
  holding_option.innerHTML = "To holding";
  at_ring_option.innerHTML = "At ring";
  competing_option.innerHTML = "Competing";

  select_menu.style = "width: 120px";
  select_menu.appendChild(empty_option);
  select_menu.appendChild(holding_option);
  select_menu.appendChild(at_ring_option);
  select_menu.appendChild(competing_option);


  if (team_match.fields.competing) {
      select_menu.value = tmdb_vars_REPORT_STATUS_COMPETING_VALUE;
  } else if (team_match.fields.at_ring) {
    select_menu.value = tmdb_vars_REPORT_STATUS_AT_RING_VALUE;
  } else if (team_match.fields.in_holding) {
    select_menu.value = tmdb_vars_REPORT_STATUS_HOLDING_VALUE;
  }
  else {
    select_menu.value = tmdb_vars_REPORT_STATUS_EMPTY_VALUE;
  }

  select_menu.name = "report_status";
  select_menu.onchange = function() {
    on_report_status_changed(this, team_match.pk);
  };

  var match_status = evaluate_status(team_match);
  if (match_status['match_status_code'] == tmdb_vars_MATCH_STATUS_CODE_COMPLETE) {
    select_menu.disabled = true;
  }

  return select_menu;
}

function render_ring_number(team_match) {
  var ring_field = document.createElement("select");
  ring_field.style = "width:50px;"

  var option = document.createElement("option");
  option.value = '';
  option.innerHTML = '---';
  ring_field.appendChild(option);
  ring_field.value = option.value;

  for (var i=1; i<=tmdb_vars_MAX_NUM_RINGS; ++i) {
    option = document.createElement("option");
    option.value = i;
    option.innerHTML = i;
    ring_field.appendChild(option);
  }

  if (team_match.fields.ring_number) {
    ring_field.value = team_match.fields.ring_number;
  }

  ring_field.onchange = function() {
    on_ring_number_changed(this, team_match.pk);
  }

  var match_status = evaluate_status(team_match);
  if (match_status['match_status_code'] == tmdb_vars_MATCH_STATUS_CODE_COMPLETE) {
    ring_field.disabled = true;
  }
  return ring_field;
}

function render_winning_team(team_match) {
  var select_menu = document.createElement("select");
  var option = document.createElement("option");
  option.value = '';
  option.innerHTML = "---";
  select_menu.style = "width:200px;";
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

function evaluate_status(team_match) {
  if (team_match.fields.winning_team != null) {
    return {
        match_status_css_class: 'team_match_complete',
        match_status_code: tmdb_vars_MATCH_STATUS_CODE_COMPLETE,
        match_status_text: "Complete"
    };
  }
  if (team_match.fields.ring_number != null) {
    if (team_match.fields.competing) {
      return {
          match_status_css_class: 'team_match_competing',
          match_status_code: 5,
          match_status_text: "Competing at ring " + team_match.fields.ring_number
      };
    }
    if (team_match.fields.at_ring) {
      return {
          match_status_css_class: 'team_match_at_ring',
          match_status_code: tmdb_vars_MATCH_STATUS_CODE_AT_RING,
          match_status_text: "At ring " + team_match.fields.ring_number
      };
    } else {
      return {
          match_status_css_class: 'team_match_sent_to_ring',
          match_status_code: tmdb_vars_MATCH_STATUS_CODE_SENT_TO_RING,
          match_status_text: "Sent to ring " + team_match.fields.ring_number
      };
    }
  }
  if (team_match.fields.in_holding) {
    return {
        match_status_css_class: 'team_match_in_holding',
        match_status_code: tmdb_vars_MATCH_STATUS_CODE_SENT_IN_HOLDING,
        match_status_text: "Report to holding"
    };
  }
  return {
      match_status_css_class: 'team_match_not_started',
      match_status_code: tmdb_vars_MATCH_STATUS_CODE_SENT_NOT_STARTED,
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
  tmdb_vars.match_update_ws.send = function() {
    alert("Operation failed. The connection to the server has been lost. Please reload the page.");
    render_updated_display();
  }
  setTimeout(function() {
    alert("Lost connection to " + tmdb_vars.match_update_ws.url + "\n\nPlease reload the page.");
  }, 5000);
}

function start_teammatch_websocket(tournament_slug, tournament_json_url) {
  if (tmdb_vars.match_update_ws != null) {
    return;
  }
  var ws_proto = "wss://"
  if (window.location.protocol == "http:") {
    ws_proto = "ws://"
  }
  var ws_url = ws_proto + window.location.host + "/tmdb/tournament/" + tournament_slug + "/match_updates/";
  tmdb_vars.tournament_data.tournament_slug = tournament_slug;
  tmdb_vars.initial_tournament_data_url = window.location.protocol + "//" + window.location.host + tournament_json_url;
  console.log("Opening connection to " + ws_url);
  tmdb_vars.match_update_ws = new WebSocket(ws_url);
  tmdb_vars.match_update_ws.onmessage = handle_message;
  tmdb_vars.match_update_ws.onopen = on_websocket_open;
  tmdb_vars.match_update_ws.onclose = on_websocket_close;
}

function on_report_status_changed(element, team_match_pk) {
  var team_match = {};
  team_match.model = 'tmdb.teammatch';
  team_match.pk = team_match_pk;
  team_match.fields = {};
  team_match.fields.in_holding = (element.value >= tmdb_vars_REPORT_STATUS_HOLDING_VALUE);
  team_match.fields.at_ring = (element.value >= tmdb_vars_REPORT_STATUS_AT_RING_VALUE);
  team_match.fields.competing = (element.value >= tmdb_vars_REPORT_STATUS_COMPETING_VALUE);
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

function get_school_name_from_team_registration(team_registration_id) {
  if (team_registration_id == null) {
    return null;
  }
  var team_registration = tmdb_vars.tournament_data.tmdb_teamregistration[team_registration_id];
  var team_id = team_registration.fields.team;
  var team = tmdb_vars.tournament_data.tmdb_team[team_id];
  return render_school_name(team.fields.school);
}
