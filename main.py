import pandas as pd
from pandas.plotting import table
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, FuncFormatter
import os
from datetime import datetime, timedelta
import math

csv_file_path = '24Rotation3.csv'
# date_strings = ['03/18/24-05/12/24']
date_strings = ['05/13/24-07/14/24']
date_string = date_strings[-1]
main_scores_start_col = 3
main_scores_end_col = 20
stats_start_col = 24
stats_end_col = 38
leaderboards_start_col = 39
leaderboards_end_col = 60
leaderboard_rows = 11
average_score_start_col = 62
average_score_end_col = 78

def format_with_commas(value, _):
    return "{:,.0f}".format(value)

def split_date_range(date_range):
    # Parse the input date range string
    start_str, end_str = date_range.split('-')
    start_date = datetime.strptime(start_str, '%m/%d/%y')
    end_date = datetime.strptime(end_str, '%m/%d/%y')

    # List to store date ranges
    date_ranges = []
    
    # Loop to create 14-day ranges
    current_start_date = start_date
    while current_start_date <= end_date:
        current_end_date = current_start_date + timedelta(days=13)  # 14 days including start date
        if current_end_date > end_date:
            current_end_date = end_date
        date_ranges.append(f'{current_start_date.strftime("%m/%d/%y")}-{current_end_date.strftime("%m/%d/%y")}')
        current_start_date = current_end_date + timedelta(days=1)  # Move to the next day after the current end date
    
    return date_ranges


def create_player_graphs(csv_file, row_index, start_col, end_col):
    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Extract the specified row and columns
    x_labels = df.iloc[0, start_col:end_col + 1].values
    y_values_str = df.iloc[row_index, start_col:end_col + 1].astype(str)

    # Replace commas with an empty string and convert to float
    y_values = y_values_str.str.replace(',', '').astype(float)
    
    # Extract the Discord username from the first row and the 'Discord' column (assuming it's in the first row and labeled 'Discord')
    discord_user = df.at[row_index, 'Discord name']

    # Append "\n {score}" to each value in x_labels
    combined_labels = [f"{x}\n{format_with_commas(y, 0)}" for x, y in zip(x_labels, y_values)]
    
    # Set the figure size with double the width
    plt.figure(figsize=(1.25 * len(x_labels), 6))
    
    # Plot the points
    plt.plot(combined_labels, y_values, marker='o', linestyle='-')

    # Add labels and title
    plt.title(f'@{discord_user} {date_string}')
    
    # Use ScalarFormatter to disable scientific notation on the y-axis
    plt.gca().yaxis.set_major_formatter(FuncFormatter(format_with_commas))       
     
    # Check if the folder exists, create it if not
    folder_path = os.path.splitext(csv_file)[0]
    subdirectory = "PlayerStats"
    full_path = os.path.join(folder_path, subdirectory)
    os.makedirs(full_path, exist_ok=True)
    
    # Save the plot as an image
    plt.savefig(f'{full_path}/{discord_user}.png')

    # Clear the plot for the next iteration
    plt.clf()
    plt.close()
    
def create_table(csv_file, df, table_name, title="", col_widths=None, leaderboard=False, player_stats=False):
    # Create a figure and axes
    num_rows, num_columns = df.shape
    figsize = (num_columns * 1.5, num_rows * 0.3)
    fig, ax = plt.subplots(figsize=figsize)
    # fig, ax = plt.subplots(figsize=(12, 8))

    # Hide the axes
    ax.axis('off')

    # Create a table and add it to the axes
    col_widths = ([0.15] * len(df.columns) if col_widths == None else col_widths)

    table_data = table(ax, df, loc='center', colWidths=col_widths)

    # Style the table
    table_data.auto_set_font_size(False)
    table_data.set_fontsize(10)
    table_data.scale(1.2, 1.2)
    
    if leaderboard:
        # Color rows based on leaderboard rankings
        colors = ['#FFD700', '#C0C0C0', '#CD7F32', '#4169E1', '#228B22']
        for i in range(1, num_rows + 1):  # Iterate over data rows
            color_index = min((i - 1) // 2, len(colors) - 1)
            for j in range(num_columns):  # Iterate over columns
                cell = table_data._cells.get((i, j))
                cell.set_facecolor(colors[color_index])
                cell_text = cell.get_text()
                cell_text.set_color('black')  # Change 'black' to your desired text color

    if player_stats:
        # Color rows based on leaderboard rankings
        colors = ['#ADD8E6', '#90EE90', '#FFFF99', '#FFB6C1', '#FFDAB9']
        color_index = 0  # Initialize color index
        for i in range(1, num_rows + 1):  # Exclude column headers, include row headers
            if color_index >= len(colors):
                color_index = 0  # Reset color index if it exceeds the length of the colors list
            for j in range(num_columns):  # Iterate over columns
                cell = table_data._cells.get((i, j))
                if cell is not None:
                    cell.set_facecolor(colors[color_index])
                    cell_text = cell.get_text()
                    cell_text.set_color('black')  # Change 'black' to your desired text color
            color_index += 1  # Move to the next color in the list
            
    # Add a title
    plt.title(f'{title}')
    
    # Check if the folder exists, create it if not
    folder_path = os.path.splitext(csv_file)[0]
    os.makedirs(folder_path, exist_ok=True)

    # Save the figure as an image
    plt.savefig(f'{folder_path}/{table_name}.png', bbox_inches='tight', pad_inches=0.5)
    
    # Clear the plot for the next iteration
    plt.clf()
    plt.close()
    
def create_player_stats_table(csv_file, start_col, end_col):
    # Read the CSV file
    raw_df = pd.read_csv(csv_file, header=None, usecols=range(start_col, end_col))
    
    # Set the first row as column headers
    raw_df.columns = raw_df.iloc[0]
    
    # Set the second column as row indices
    raw_df = raw_df.set_index(raw_df.columns[1])
    
    # Drop the first 2 rows
    raw_df = raw_df.drop(raw_df.index[0])
    raw_df = raw_df.drop(raw_df.index[0])

    # Filter the DataFrame based on who wants to be included
    df = raw_df[raw_df["public?"] == "y"]

    # Drop the first column with "public?"
    df = df.drop(df.columns[0], axis=1)
    
    # Select specific columns for the first table
    table1_columns = [0, 1, 8, 9, 10, 11]
    df1 = df.iloc[:, table1_columns]
    
    # Select the rest of the columns for the second table
    table2_columns = [col for col in range(len(df.columns)) if col not in table1_columns]
    df2 = df.iloc[:, table2_columns]
    
    # Specify the column widths
    col_widths1 = [0.1, 0.15, 0.15, 0.15, 0.15, 0.15]
    col_widths2 = [0.167, 0.167, 0.167, 0.167, 0.167, 0.167]
        
    create_table(csv_file, df1, "statistics1", f"Player score stats {date_string}", col_widths1, False, True)
    create_table(csv_file, df2, "statistics2", f"Player GQ completions {date_string}", col_widths2, False, True)

def create_leaderboards_table(csv_file, start_col, end_col, num_rows):
    # Read the CSV file
    df = pd.read_csv(csv_file, header=None, usecols=range(start_col, end_col), skiprows=42, nrows=num_rows)
    
    # Set the first row as column headers
    df.columns = df.iloc[0]

    # Set the first column as row indices
    df = df.set_index(df.columns[0])

    # Drop the first row
    df = df.drop(df.index[0])
    
    # Initialize section count
    date_ranges = split_date_range(date_string)
    section_count = len(date_ranges)
    cols_per_section = 4
    
    # Split the DataFrame into four quarters
    num_columns = len(df.columns)
    quarter_size = num_columns // 4

    # Create a list to store the four DataFrames
    quarter_dfs = []

    for i in range(section_count):
        start_col = i * cols_per_section
        end_col = (i + 1) * cols_per_section
        quarter_df = df.iloc[:, start_col:end_col]
        quarter_dfs.append(quarter_df)
        
    # Specify the column widths
    col_widths = []
    for i in range(section_count):
        col_widths.append(0.25)
        
    # Create and save an image for each quarter
    for i, quarter_df in enumerate(quarter_dfs):
        create_table(csv_file, quarter_df, f'leaderboards{i+1}', f'Leaderboards {date_ranges[i]}', col_widths, True)
    
    
def create_average_scores_graph(csv_file, start_col, end_col):
    # Read the CSV file
    df = pd.read_csv(csv_file, header=None, usecols=range(start_col, end_col), skiprows=42, nrows=2)
    
    # Extract the specified row and columns
    x_labels = df.iloc[0, :].values
    y_values_str = df.iloc[1, :].astype(str)

    # Replace commas with an empty string and convert to float
    y_values = y_values_str.str.replace(',', '').astype(float)

    # Append "\n {score}" to each value in x_labels
    combined_labels = [f"{x}\n{format_with_commas(y, 0)}" for x, y in zip(x_labels, y_values)]
    
    # Set the figure size with double the width
    plt.figure(figsize=(1.25 * len(x_labels), 6))
    
    # Plot the points
    plt.plot(combined_labels, y_values, marker='o', linestyle='-')

    # Add labels and title
    plt.title(f'Average C45 + C44 Scores {date_string}')
    
    # Use ScalarFormatter to disable scientific notation on the y-axis
    plt.gca().yaxis.set_major_formatter(FuncFormatter(format_with_commas))       
     
    # Check if the folder exists, create it if not
    folder_path = os.path.splitext(csv_file)[0]
    os.makedirs(folder_path, exist_ok=True)
    
    # Adding annotation at the bottom
    plt.annotate('*Averages were done over non-zero scores', xy=(1, -0.1), ha='right', va='center', xycoords='axes fraction', fontsize=7, color='black')

    # Save the plot as an image
    plt.savefig(f'{folder_path}/average_scores.png')

    # Clear the plot for the next iteration
    plt.clf()
    plt.close()


for i in range(1, 40):
    create_player_graphs(csv_file_path, row_index=i, start_col=main_scores_start_col, end_col=main_scores_end_col)
create_leaderboards_table(csv_file_path, start_col=leaderboards_start_col, end_col=leaderboards_end_col, num_rows=leaderboard_rows)
create_player_stats_table(csv_file_path, start_col=stats_start_col, end_col=stats_end_col)
create_average_scores_graph(csv_file_path, start_col=average_score_start_col, end_col=average_score_end_col)
