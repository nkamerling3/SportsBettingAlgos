import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
import rebounding_data as rebound

#Set Global Variables


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # team_df = rebound.get_team_rebounding_data("PHI", 2023)
    # print(player_df)
    # print(team_df)
    team_list = np.array(['ATL', 'BOS', 'BRK', 'CHO', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC',
                          'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC',
                          'SAS', 'TOR', 'UTA', 'WAS'])
    # rebound.store_team_rebound_data(2023, team_list, verbose=True) #only run when need new data

    league_df, league_df_home, league_df_away = rebound.create_league_data_structure()
    player_df, player_home_df, player_away_df = rebound.get_player_rebound_data("Tobias Harris", 2023,
                                                                                league_df, league_df_home, league_df_away)