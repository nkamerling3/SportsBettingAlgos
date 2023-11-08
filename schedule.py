import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
from datetime import datetime


def get_weekly_schedule(week):
    #setup and create df to store weekly games
    team_names = ['Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets', 'Chicago Bulls',
                  'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets', 'Detroit Pistons',
                  'Golden State Warriors', 'Houston Rockets', 'Indiana Pacers', 'Los Angeles Clippers',
                  'Los Angeles Lakers', 'Memphis Grizzlies', 'Miami Heat', 'Milwaukee Bucks', 'Minnesota Timberwolves',
                  'New Orleans Pelicans', 'New York Knicks', 'Oklahoma City Thunder', 'Orlando Magic',
                  'Philadelphia 76ers', 'Phoenix Suns', 'Portland Trail Blazers', 'Sacramento Kings',
                  'San Antonio Spurs', 'Toronto Raptors', 'Utah Jazz', 'Washington Wizards']
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    data = {}

    # Initialize the DataFrame with 0s
    for day in days_of_week:
        data[day] = [''] * len(team_names)

    # Create the DataFrame
    week_schedule_df = pd.DataFrame(data, index=team_names)
    # week must be formatted like this:  w3

    url_initial = "https://theathletic.com/nba/schedule/"
    # url = "https://theathletic.com/nba/schedule/2023-11-05/"
    url = "https://hashtagbasketball.com/advanced-nba-schedule-grid"
    # Send an HTTP GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        # table_id = "ContentPlaceHolder1_w3_GridView1"
        table_id = "ContentPlaceHolder1_" + week + "_GridView1"

        schedule_table = soup.find('table', {'id': table_id})


        # Check if the table was found
        if schedule_table:
            # Extract and process the data from the table
            for row in schedule_table.find_all('tr'):
                columns = row.find_all('td')
                # Process the columns as needed
                team_flag = False
                team = ''
                count = 0
                for column in columns:
                    print(column.text)  # Print the text content of each column
                    if team_flag:
                        count += 1
                    if is_team_name(column.text, team_names) and not team_flag:
                        team_flag = True
                        team = column.text
                    if 2 <= count <= 8:
                        if column.text != "\xa0":
                            week_schedule_df.at[team, week_schedule_df.columns[count-2]] = column.text

            week_schedule_df.to_csv('./nba_weekly_schedule.csv', index=False)
            return week_schedule_df
        else:
            print("Table not found on the page.")
    else:
        print("Failed to retrieve data from the URL.")


def is_team_name(string, team_names):
    for team in team_names:
        if team == string:
            return True
    return False