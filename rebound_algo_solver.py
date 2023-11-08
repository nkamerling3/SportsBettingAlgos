import pandas as pd

import rebounding_utils as rebound
import schedule
import datetime



def dtrmn_fair_odds(verbose=False):

    #creates df of players
    players_df = rebound.create_player_df(verbose=True)
    if verbose:
        print("players df:")
        print(players_df)

    #read from .csv if df has already been created
    players_df = pd.read_csv('./nba_players_2024.csv')

    #update players_df so that it includes proper team abbreviations
    players_df, abbrev_table = rebound.add_abbreviations(players_df)

    #creates weekly schedule of games
    date_string = "2023-11-06"
    week = 'w3'  # update each week of nba season, go to website to see date ranges for each week
    week_schedule_df = schedule.get_weekly_schedule(week)
    if verbose:
        print('weekly schedule')
        print(week_schedule_df)

    #Finds out which players have a game today and adds opponents and Home/Away to df
    #all players that do not have games are removed from df
    players_df = rebound.find_opponent(players_df, week_schedule_df, abbrev_table)

    #Update model for all players that have game today

    #Update 2023 model(should only have to do this once)
    #Update 2024 model (should have to do this each time a player has a new game)

    #Determines rebound probability distribution from running simulations with random decision trees

    #Determines chances of getting more than 0-20 rebounds and calculates fair odds (increments of 0.5 for betting sites)

    #Determines chances of getting less than 0-20 rebounds and calculates fair odds (increments of 0.5 for betting sites)

    #Writes all data to .csv file
    pass


if __name__ == '__main__':
    dtrmn_fair_odds()


