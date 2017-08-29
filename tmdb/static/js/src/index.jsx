//import React from 'react';
//import ReactDOM from 'react-dom';

class HeaderRow extends React.Component {
    render() {
         return (<thead>
            <tr>
                <th> Match No.</th>
                <th> Round</th>
                <th> Blue Team</th>
                <th> Red Team</th>
                <th> In Holding? </th>
                <th> Ring No.</th>
                <th> Winning Team</th>
                <th> Status</th>
            </tr>
         </thead>);
    }
}

class MatchRow extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            match_number: '101',
            round: 'X',
            blue_team: 'Team A',
            red_team: 'Team B',
            ring_num: '123',
            in_holding: false,
            winning_team: 'None',
            status: 'no clue'
        };
    }

    populate_row(match_data) {
        this.setState({
            match_number: match_data['match_number'],
            round: match_data['round'],
            blue_team: match_data['blue_team'],
            red_team: match_data['red_team'],
            ring_num: match_data['ring_num'],
            in_holding: match_data['in_holding'],
            winning_team: match_data['winning_team'],
            status: match_data['status']
        });
    }

    render(props) {
        return (
            <tr>
             <td> {this.state.match_number} </td>
             <td> {this.state.round} </td>
             <td> {this.state.blue_team} </td>
             <td> {this.state.red_team} </td>
             <td> {this.state.ring_num} </td>
             <td> <input type="checkbox" checked={this.state.in_holding} /> </td>
             <td> {this.state.winning_team} </td>
             <td> {this.state.status} </td>
            </tr>
        );
    }
}

class MatchTable extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            data: []
        }
    }

	render() {
		return (
		<div>
		    <h1> Test </h1>
		    <table class="table table-striped table">
                <HeaderRow />
                <tbody>
		            <MatchRow match_data={this.populate_row} />
		            <MatchRow />
		        </tbody>
		    </table>
		</div>
		);
	}
};



ReactDOM.render(
	<MatchTable />,
	document.getElementById('match-table')
);

