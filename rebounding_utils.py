import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
from datetime import datetime
import re
import urllib
from urllib.parse import urlparse
import urllib.request
import numpy as np
import datetime as dt


def get_player_rebound_data(player_name, season, league_df, league_df_home, league_df_away, verbose=False):
    url_initial = 'https://www.basketball-reference.com/players/'
    firstname, lastname = player_name.split()
    firstname_url = firstname[:2].lower()
    lastname_url = lastname[:5].lower()
    lastname_letter = lastname[:1].lower()
    year = season
    year_string = str(year)
    version = 1
    max_attempts = 5
    attempts = 0
    url_final = url_initial
    url_final = (url_initial + lastname_letter + "/" + lastname_url + firstname_url + "0" +
                 str(version) + "/gamelog/" + year_string)
    while attempts < max_attempts:
        try:

            # Send an HTTP GET request to the URL
            response = requests.get(url_final)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find the table that contains Joel Embiid's game log
                game_log_table = soup.find('table', {'id': 'pgl_basic'})

                # Initialize df
                player_df = pd.DataFrame(columns=['Date', 'Opponent', 'Offensive Rebounds', 'Defensive Rebounds',
                                                  'Total Rebounds', 'Home/Away'])

                #Determine correct player
                player_found = False
                for row in game_log_table.find_all('tr')[1:]:
                    columns = row.find_all('td')
                    date = columns[1].text
                    home_away = columns[4].text
                    player_found = True #If makes it here player has been found
                    break

                #If makes it through loop then player has been found
                # player_found = True
                if player_found:
                    if verbose:
                        print(f"Player found!, version was {version}")
                    break
            else:
                print("player request failed")
                print(f"Failed to retrieve data. Status code: {response.status_code}")

        except Exception as e:
            if verbose:
                print(e)
            attempts += 1
            version += 1
            url_final = (url_initial + lastname_letter + "/" + lastname_url + firstname_url + "0" +
                         str(version) + "/gamelog/" + year_string)
            if attempts >= max_attempts:
                print("Max attempts reached. Exiting.")
                break

    # Iterate through the table rows to extract rebound data
    for row in game_log_table.find_all('tr')[1:]:  # Skip the header row
        columns = row.find_all('td')
        if verbose:
            print(columns)
        if len(columns) != 0:
            date = columns[1].text
            home_away = columns[4].text
            opponent = columns[5].text
            if '@' in home_away:
                home_away = 'Away'
            else:
                home_away = "Home"
            dnp = columns[7].text
            if verbose:
                print(dnp)
            strings_to_check = ["Did Not Dress", "Did Not Play", "Inactive"]
            # if "Did Not Dress" and 'Did Not Play' and 'Inactive' not in dnp:
            if all(string not in dnp for string in strings_to_check):
                o_rebounds = columns[18].text  # The 17th column contains rebounds
                d_rebounds = columns[19].text
                t_rebounds = columns[20].text
                # rebounds_per_game.append((date, rebounds))
                new_row = {'Date': date, 'Opponent': opponent, 'Offensive Rebounds': o_rebounds,
                           'Defensive Rebounds': d_rebounds, 'Total Rebounds': t_rebounds, 'Home/Away': home_away}
                player_df.loc[player_df.shape[0]] = new_row
                if verbose:
                    print(player_df)

    #change total rebounds to integer
    player_df['Total Rebounds'] = player_df['Total Rebounds'].astype(float)

    #add days rest to df
    player_df['Date'] = pd.to_datetime(player_df['Date'])
    player_df['Rest Days'] = (player_df['Date'] - player_df['Date'].shift(1)).dt.days.fillna(2)
    # player_df['Date'] = player_df['Date'].dt.date
    player_df['Date'] = player_df['Date'].dt.strftime('%Y-%m-%d')\

    #add SMA of player rebounds
    ma_length = 10
    player_df['Rebounds Total MA'] = player_df['Total Rebounds'].rolling(window=ma_length).mean()
    player_df['Cumulative Total Rebounds'] = player_df['Total Rebounds'].cumsum()
    for i in range(0, ma_length - 1):
        player_df.loc[i, 'Rebounds Total MA'] = player_df.loc[i, 'Cumulative Total Rebounds'] / (i + 1)

    #shift rebound ma by one so aren't looking in to future
    player_df['Rebounds Total last 10'] = player_df['Rebounds Total MA'].shift(1).fillna(
        player_df['Total Rebounds'].mean())

    #split into home and away dataframes
    player_away_df = player_df[player_df['Home/Away'] == 'Away']
    player_home_df = player_df[player_df['Home/Away'] == 'Home']
    player_away_df = player_away_df.reset_index(drop=True)  # reset index
    player_home_df = player_home_df.reset_index(drop=True)  # reset index


    # Add data from opponents
    player_df = add_opponent_data(player_df, league_df, verbose=False)
    player_home_df = add_opponent_data(player_home_df, league_df_away, verbose=False)
    player_away_df = add_opponent_data(player_away_df, league_df_home, verbose=False)


    return player_df, player_home_df, player_away_df


def get_team_rebounding_data(team_abbreviation, season, verbose=False):
    # Define the URL for the Sixers' game log on Basketball Reference for the 2022 season
    # url = 'https://www.basketball-reference.com/teams/PHI/2023/gamelog/'
    url_initial = 'https://www.basketball-reference.com/teams/'
    url = url_initial + team_abbreviation + "/" + str(season) + "/gamelog"

    # Send an HTTP GET request to the URL
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table that contains the Sixers' game log
        game_log_table = soup.find('table', {'id': 'tgl_basic'})

        # Initialize team df
        team_df = pd.DataFrame(columns=['Date', 'Opponent', 'Offensive Rebounds Allowed', 'Total Rebounds Allowed',
                                        'Home/Away'])

        # Iterate through the table rows to extract rebounds allowed
        for row in game_log_table.find_all('tr')[2:]:  # Skip the header row
            columns = row.find_all('td')
            if verbose:
                print(columns)
            if len(columns) != 0:
                date = columns[1].text
                opponent = columns[3].text
                home_away = columns[2].text
                if '@' in home_away:
                    home_away = 'Away'
                else:
                    home_away = "Home"
                total_rebounds_allowed = float(columns[34].text)  # The 15th column contains rebounds allowed
                o_rebound_allowed = float(columns[33].text)
                new_row = {'Date': date, 'Opponent': opponent, "Offensive Rebounds Allowed": o_rebound_allowed,
                           "Total Rebounds Allowed": total_rebounds_allowed, "Home/Away": home_away}
                team_df.loc[team_df.shape[0]] = new_row
                if verbose:
                    print(team_df)

        team_df['Defensive Rebounds Allowed'] = team_df['Total Rebounds Allowed'] - team_df['Offensive Rebounds Allowed']

        #set team data to datetime
        # team_df['Date'] = pd.to_datetime(team_df['Date'])
        # team_df['Date'] = team_df['Date'].dt.date
        #set home and away df
        team_away_df = team_df[team_df['Home/Away'] == 'Away']
        team_home_df = team_df[team_df['Home/Away'] == 'Home']
        team_away_df = team_away_df.reset_index(drop=True)  # reset index
        team_home_df = team_home_df.reset_index(drop=True)  # reset index

        #perform calculations
        ma_length = 10
        team_df['Rebounds Allowed MA'] = team_df['Total Rebounds Allowed'].rolling(window=ma_length).mean()
        team_away_df['Rebounds Allowed MA'] = team_away_df['Total Rebounds Allowed'].rolling(window=ma_length).mean()
        team_home_df['Rebounds Allowed MA'] = team_home_df['Total Rebounds Allowed'].rolling(window=ma_length).mean()

        #Account for nan values just make them equal to mean of past results
        team_df['Cumulative Total Rebounds'] = team_df['Total Rebounds Allowed'].cumsum()
        team_away_df['Cumulative Total Rebounds'] = team_away_df['Total Rebounds Allowed'].cumsum()
        team_home_df['Cumulative Total Rebounds'] = team_home_df['Total Rebounds Allowed'].cumsum()
        # team_df.loc[0:ma_length-1, 'Rebounds Allowed MA'] = team_df.loc[0:ma_length-1, 'Cumulative Total Rebounds']/(range(1, ma_length))
        # team_df['Rebounds Allowed MA'] = (team_df['Cumulative Total Rebounds'].iloc[:ma_length-1] /
        #                                   (team_df.index[:ma_length-1] + 1))
        #non_vectorized
        for i in range(0, ma_length-1):
            team_df.loc[i, 'Rebounds Allowed MA'] = team_df.loc[i, 'Cumulative Total Rebounds']/(i + 1)
            team_away_df.loc[i, 'Rebounds Allowed MA'] = team_away_df.loc[i, 'Cumulative Total Rebounds'] / (i + 1)
            team_home_df.loc[i, 'Rebounds Allowed MA'] = team_home_df.loc[i, 'Cumulative Total Rebounds'] / (i + 1)

        # shift rebound ma by one so aren't looking in to future
        team_df['Rebounds Allowed Last 10'] = team_df['Rebounds Allowed MA'].shift(1).fillna(
            team_df['Total Rebounds Allowed'].mean())
        team_away_df['Rebounds Allowed Last 10'] = team_away_df['Rebounds Allowed MA'].shift(1).fillna(
            team_away_df['Total Rebounds Allowed'].mean())
        team_home_df['Rebounds Allowed Last 10'] = team_home_df['Rebounds Allowed MA'].shift(1).fillna(
            team_home_df['Total Rebounds Allowed'].mean())

        return team_df, team_away_df, team_home_df

    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")


def store_team_rebound_data(year, teams, verbose=False):
    for team in teams:
        if verbose:
            print(datetime.now())
            print(team)
        request_interval = 5
        team_df, team_away_df, team_home_df = get_team_rebounding_data(team, year)
        file_name = './Training_Data/' + team + "_" + str(year) + "_training_data.csv"
        away_file_name = './Training_Data/Away/' + team + "_" + str(year) + "_training_data_away.csv"
        home_file_name = './Training_Data/Home/' + team + "_" + str(year) + "_training_data_home.csv"
        team_df.to_csv(file_name, index=False)
        team_away_df.to_csv(away_file_name, index=False)
        team_home_df.to_csv(home_file_name, index=False)
        if verbose:
            print(team_df)
        time.sleep(request_interval)


def store_player_rebound_data(year, player_list, verbose=False):
    for player in player_list:
        if verbose:
            print(datetime.now())
            print(player)
        request_interval = 5
        firstname, lastname = player.split()
        player_df, player_away_df, player_home_df = get_player_rebound_data(player, year)
        file_name = './Training_Data/' + str(firstname) + "_" + str(lastname) + "_" + str(year) + "_training_data.csv"
        away_file_name = './Training_Data/Away/' + str(firstname) + "_" + str(lastname) + "_" + str(year) + "_training_data_away.csv"
        home_file_name = './Training_Data/Home/' + str(firstname) + "_" + str(lastname) + "_" + str(year) + "_training_data_home.csv"
        player_df.to_csv(file_name, index=False)
        player_away_df.to_csv(away_file_name, index=False)
        player_home_df.to_csv(home_file_name, index=False)
        if verbose:
            print(player_df)
        time.sleep(request_interval)


def add_opponent_data(player_df, league_df, verbose=False):
    for index, row in player_df.iterrows():
        date = row['Date']
        opponent = row['Opponent']
        opponent_df = league_df[opponent]
        game = opponent_df[opponent_df['Date'] == date]
        opponent_rebounds_allowed = game['Rebounds Allowed Last 10']
        if verbose:
            print(opponent_rebounds_allowed)
            print(game.index[0])
        opponent_rebounds_allowed = game['Rebounds Allowed Last 10'][game.index[0]]
        player_df.loc[index, 'Opponent Rebounds Allowed Last 10'] = opponent_rebounds_allowed
        if verbose:
            print(index)
            print(player_df)
    return player_df


def create_league_data_structure():
    league_df = {}
    league_df_home = {}
    league_df_away = {}
    directory_path = "./Training_Data"
    directory_path_home = "./Training_Data/Home"
    directory_path_away = "./Training_Data/Away"
    team_files = os.listdir(directory_path)
    team_files_home = os.listdir(directory_path_home)
    team_files_away = os.listdir(directory_path_away)

    for file in team_files:
        file_path = os.path.join(directory_path, file)
        if os.path.isfile(file_path):
            team_name = file_path.split("\\")[1][:3]
            team_df = pd.read_csv(file_path)
            league_df[team_name] = team_df

    for file in team_files_home:
        file_path = os.path.join(directory_path_home, file)
        if os.path.isfile(file_path):
            team_name = file_path.split("\\")[1][:3]
            team_df = pd.read_csv(file_path)
            league_df_home[team_name] = team_df

    for file in team_files_away:
        file_path = os.path.join(directory_path_away, file)
        if os.path.isfile(file_path):
            team_name = file_path.split("\\")[1][:3]
            team_df = pd.read_csv(file_path)
            league_df_away[team_name] = team_df

    return league_df, league_df_home, league_df_away


def create_player_df(verbose=False):
    # setup and create df to store player names and teams
    data = {'Player': [], 'Team': []}
    player_df = pd.DataFrame(data)
    # update the DataFrame
    url = 'https://basketball.realgm.com/nba/players'
    # parsed_url = urlparse(url)
    # with urllib.request.urlopen(url) as res:
    #     html_content = res.read()
    response = requests.get(url)
    # Check if the request was successful
    #alternate method html code
    # soup2 = BeautifulSoup(html_content, 'html.parser')
    # table_id = "table-2929"
    # player_table = soup2.find('table', {'id': table_id})

    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        table_class = "tablesaw"
        player_table = soup.find('table', {'class': table_class})
        tables = soup.find_all('table')
        # Check if the table was found
        if player_table:
            # Extract and process the data from the table
            for row in player_table.find_all('tr'):
                columns = row.find_all('td')
                count = 0
                player = ''
                team = ''
                for column in columns:
                    if verbose:
                        print(column.text)
                    if count == 1:
                        player = column.text
                    if count == 6:
                        team = column.text
                    count += 1
                if len(columns) > 0:
                    player_df.loc[player_df.shape[0]] = {'Player': player, 'Team': team}
            player_df.to_csv('./nba_players_2024.csv', index=False)
            return player_df
        else:
            print("Table not found on the page.")
    else:
        print("Failed to retrieve data from the URL.")


def add_abbreviations(players_df, verbose=False):
    abbrev_dict = {}
    team_names = np.array(['Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets', 'Chicago Bulls',
                           'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets', 'Detroit Pistons',
                           'Golden State Warriors', 'Houston Rockets', 'Indiana Pacers', 'Los Angeles Clippers',
                           'Los Angeles Lakers', 'Memphis Grizzlies', 'Miami Heat', 'Milwaukee Bucks',
                           'Minnesota Timberwolves', 'New Orleans Pelicans', 'New York Knicks', 'Oklahoma City Thunder',
                           'Orlando Magic', 'Philadelphia Sixers', 'Phoenix Suns', 'Portland Trail Blazers',
                           'Sacramento Kings', 'San Antonio Spurs', 'Toronto Raptors', 'Utah Jazz',
                           'Washington Wizards'])
    schedule_abbrev = np.array(['ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GS', 'HOU', 'IND',
                                'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NO', 'NY', 'OKC', 'ORL', 'PHI', 'PHO',
                                'POR', 'SAC', 'SA', 'TOR', 'UTA', 'WAS'])
    reference_abbrev = np.array(['ATL', 'BOS', 'BRK', 'CHO', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND',
                                 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO',
                                 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS'])

    abbrev_table = pd.DataFrame({'Team Name': team_names, 'Schedule Abbrev': schedule_abbrev,
                                 'Reference Abbrev': reference_abbrev})
    for i in range(len(team_names)):
        abbrev_dict[team_names[i]] = [schedule_abbrev[i], reference_abbrev[i]]

    if verbose:
        print(abbrev_dict)

    schedule_column = np.empty(30)
    ref_column = np.empty(30)

    #non-vectorzied
    # for i in range(players_df.shape[0]):
    #     schedule_column[i] = abbrev_dict[players_df.iloc[i, 1]][0]
    #     ref_column[i] = abbrev_dict[players_df.iloc[i,1]][1]
    # players_df['Schedule Abbrev'] = schedule_column
    # players_df['Ref Column'] = ref_column

    players_df['Schedule Abbrev'] = players_df['Team'].map(lambda x: abbrev_dict.get(x, [None, None])[0])
    players_df['Ref Abbrev'] = players_df['Team'].map(lambda x: abbrev_dict.get(x, [None, None])[1])

    return players_df, abbrev_table


def find_opponent(player_df, week_df, abbrev_table):
    current_date = dt.date.today() + dt.timedelta(days=1)
    day_of_week = current_date.strftime('%A')
    day_df = week_df[day_of_week]
    for i in range(player_df.shape[0]):
        team = player_df.iloc[i, 1]
        opponent = day_df.loc[team]
        home_away = 'Home'
        if '@' in opponent:
            home_away = 'Away'
            opponent = opponent[1:]
        #add home/away and opponent ref abbrev to player df
    return player_df
