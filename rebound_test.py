import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
import rebounding_utils as rebound
import LinRegLearner as lrl
import DTLearner as dt
import DTLinRegCombo as dt_lrl
import matplotlib.pyplot as plt
import math
import RTLearner as rt
import BagLearner as bag

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
    player = "Tyrese Maxey"
    year = 2023
    league_df, league_df_home, league_df_away = rebound.create_league_data_structure()
    player_df, player_home_df, player_away_df = rebound.get_player_rebound_data(player, year,
                                                                                league_df, league_df_home,
                                                                                league_df_away)
    print(player_df)
    print(player_home_df)
    print(player_away_df)

    # import linreg learner
    lrLearner = lrl.LinRegLearner()

    # plot total data

    # Plot the data points
    x = player_df['Opponent Rebounds Allowed Last 10'].values
    y = player_df['Total Rebounds'].values.astype('float')
    # print(x.dtype)
    # print(y.dtype)
    plt.scatter(x, y, label='Data', color='b')
    slope, intercept = lrLearner.add_evidence(x, y)
    # Plot the best-fit line
    x_line = x
    y_line = x * slope + intercept
    plt.plot(x_line, y_line, label=f'Best Fit Line (y = {slope:.2f}x + {intercept:.2f})', color='r')

    # Add labels and a legend
    plt.xlabel('Opponent Rebounds Allowed Last 10')
    plt.ylabel('Total Rebounds by Player')
    plt.legend()
    title_string = player + " Rebounding All Data " + str(year)
    plt.title(title_string)
    correlation = np.corrcoef(x, y)[0, 1]
    print(correlation)
    plt.figtext(.3, .73, f'Correlation = {correlation:.4f}', fontsize=12, ha='center')
    figure_title = "./Plots/" + player + "_" + str(year) + "_" "Rebounding_All.png"
    plt.savefig(figure_title)
    # Show the plot
    # plt.show()
    plt.clf()

    # plot home data
    x = player_home_df['Opponent Rebounds Allowed Last 10'].values
    y = player_home_df['Total Rebounds'].values.astype('float')
    plt.scatter(x, y, label='Data', color='b')
    slope, intercept = lrLearner.add_evidence(x, y)
    # Plot the best-fit line
    x_line = x
    y_line = x * slope + intercept
    plt.plot(x_line, y_line, label=f'Best Fit Line (y = {slope:.2f}x + {intercept:.2f})', color='r')

    # Add labels and a legend
    plt.xlabel('Opponent Rebounds Allowed Last 10')
    plt.ylabel('Total Rebounds by Player')
    plt.legend()
    title_string = player + " Rebounding Home Data " + str(year)
    plt.title(title_string)
    correlation = np.corrcoef(x, y)[0, 1]
    print(correlation)
    plt.figtext(.3, .73, f'Correlation = {correlation:.4f}', fontsize=12, ha='center')
    figure_title = "./Plots/" + player + "_" + str(year) + "_" "Rebounding_Home.png"
    plt.savefig(figure_title)
    # Show the plot
    # plt.show()
    plt.clf()

    # plot away data
    x = player_away_df['Opponent Rebounds Allowed Last 10'].values
    y = player_away_df['Total Rebounds'].values.astype('float')
    plt.scatter(x, y, label='Data', color='b')
    slope, intercept = lrLearner.add_evidence(x, y)
    # Plot the best-fit line
    x_line = x
    y_line = x * slope + intercept
    plt.plot(x_line, y_line, label=f'Best Fit Line (y = {slope:.2f}x + {intercept:.2f})', color='r')

    # Add labels and a legend
    plt.xlabel('Opponent Rebounds Allowed Last 10')
    plt.ylabel('Total Rebounds by Player')
    plt.legend()
    title_string = player + " Rebounding Away Data " + str(year)
    plt.title(title_string)
    correlation = np.corrcoef(x, y)[0, 1]
    print(correlation)
    plt.figtext(.3, .73, f'Correlation = {correlation:.4f}', fontsize=12, ha='center')
    figure_title = "./Plots/" + player + "_" + str(year) + "_" "Rebounding_Away.png"
    plt.savefig(figure_title)
    # Show the plot
    # plt.show()
    plt.clf()

    #Set up training data (first half)
    player_df['Home/Away'] = player_df['Home/Away'].replace({'Home': 1, 'Away': 0})
    midpoint = player_df.shape[0] // 2
    player_training_df = player_df[:midpoint]
    player_training_df = player_training_df[['Total Rebounds', 'Home/Away', 'Rest Days', 'Rebounds Total last 10',
                                             'Opponent Rebounds Allowed Last 10']]
    print(player_training_df)
    player_training_array = player_training_df.values
    print(player_training_array)
    y_train_data = player_training_array[:, 0]
    x_train_data = player_training_array[:, 1:]

    #Set up testing data (last half)
    player_test_df = player_df[midpoint:]
    player_test_df = player_test_df[['Total Rebounds', 'Home/Away', 'Rest Days', 'Rebounds Total last 10',
                                             'Opponent Rebounds Allowed Last 10']]
    print(player_test_df)
    player_test_array = player_test_df.values
    print(player_test_array)
    y_test_data = player_test_array[:, 0]
    x_test_data = player_test_array[:, 1:]

    #Experiment Decision trees with different leaf sizes
    for i in range(1, 20):
        dt_learner = dt.DTLearner(leaf_size=i, verbose=False)
        dt_learner.add_evidence(x_train_data, y_train_data)

        #Training Data
        pred_y_train = dt_learner.query(x_train_data)  # get the predictions
        # errors = (train_y - pred_y)
        rmse_train = math.sqrt(((y_train_data - pred_y_train) ** 2).sum() / y_train_data.shape[0])
        c_train = np.corrcoef(pred_y_train, y=y_train_data)

        #Testing Data
        pred_y_test = dt_learner.query(x_test_data)  # get the predictions
        # errors = (train_y - pred_y)
        rmse_test = math.sqrt(((y_test_data - pred_y_test) ** 2).sum() / y_train_data.shape[0])
        c_test = np.corrcoef(pred_y_test, y=y_test_data)

        #Print out results
        print("RESULTS")
        print(f"Leaf Size: {i}")
        print(f"rmse train: {rmse_train}")
        print(f"c_train: {c_train[0,1]}")
        print(f"rmse test: {rmse_test}")
        print(f"c_test: {c_test[0, 1]}")
        print()


    #Experiment with random trees/bagging
    # Experiment with one point finding min and max of solvers
    y_test_data_one_point = np.array(player_test_array[1, 0])
    x_test_data_one_point = player_test_array[1, 1:]
    x_test_data_one_point = x_test_data_one_point.reshape(1,4)
    rebound_solver_possibilities = []
    for i in range(2,11):
        baglearner = bag.BagLearner(learner=rt.RTLearner, kwargs={"leaf_size": i, "verbose": False}, bags=20, boost=False,
                                    verbose=False)
        baglearner.add_evidence(x_train_data, y_train_data)

        # Training Data
        pred_y_train = baglearner.query(x_train_data)  # get the predictions
        # errors = (train_y - pred_y)
        rmse_train = math.sqrt(((y_train_data - pred_y_train) ** 2).sum() / y_train_data.shape[0])
        c_train = np.corrcoef(pred_y_train, y=y_train_data)

        # Testing Data
        pred_y_test = baglearner.query(x_test_data)  # get the predictions
        # errors = (train_y - pred_y)
        rmse_test = math.sqrt(((y_test_data - pred_y_test) ** 2).sum() / y_train_data.shape[0])
        c_test = np.corrcoef(pred_y_test, y=y_test_data)


        #Print Results
        print("RESULTS BAG LEARNER")
        print(f"Leaf Size: {i}")
        print(f"rmse train: {rmse_train}")
        print(f"c_train: {c_train[0, 1]}")
        print(f"rmse test: {rmse_test}")
        print(f"c_test: {c_test[0, 1]}")
        print()

        # One Point Min/Max Test
        # Testing Data
        pred_y_test = baglearner.query(x_test_data_one_point, make_list=True)  # get the predictions
        # errors = (train_y - pred_y)
        rmse_test = math.sqrt(((y_test_data_one_point - pred_y_test) ** 2).sum() / y_train_data.shape[0])
        bag_possibilities = baglearner.get_bag_query_list()
        bag_possibilities.sort()
        rebound_solver_possibilities += bag_possibilities

    rebound_solver_possibilities.sort()
    print(rebound_solver_possibilities)
    print(len(rebound_solver_possibilities))
    bin_range = range(0, int(max(rebound_solver_possibilities) + 2))
    plt.hist(rebound_solver_possibilities, bins=bin_range, color='blue', edgecolor='black')

    # Customize the plot (optional)
    plt.title('Rebound Simulations')
    plt.xlabel('Values')
    plt.ylabel('Frequency')
    plt.show()







