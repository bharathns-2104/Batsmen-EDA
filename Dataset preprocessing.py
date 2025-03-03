import pandas as pd
import csv

import pandas as pd
import re

# Load the CSV file (adjust the path as necessary)
df = pd.read_csv('Scraped_Dataset.csv')

# Regex pattern to capture the team name inside parentheses
team_pattern = re.compile(r'\((.*?)\)')

# List to store the extracted team names
team_names = []

# Loop through the rows, starting from the 3rd row, and extracting team names from every odd row
for index, row in df.iterrows():
    if index % 2 == 1:  # Check if the row is odd (1-based)
        team_match = team_pattern.search(row['Player'])  # Assuming the 'Player' column contains the team name
        if team_match:
            team_name = team_match.group(1)  # Extract the team name without parentheses
            team_names.append(team_name)
        else:
            team_names.append('')
    else:
        team_names.append('')  # Append an empty string for even rows

# Add the team names as a new column in the DataFrame
df['Team Name'] = team_names

# Clean the 'Player' column by removing the team name in parentheses from odd rows
df['Player'] = df['Player'].str.replace(r'\(.*?\)', '', regex=True).str.strip()

# Save the modified DataFrame back to a CSV file (optional)
#df.to_csv('updated_file.csv', index=False)

# Display the updated DataFrame to verify the result
df['Team Name'] = df['Team Name'].shift(-1)
df=df.iloc[2::2]

#print(df)

df = df.loc[:, ~df.columns.str.contains('^Unnamed')]


df['Not Out']=df['Runs'].apply(lambda x:1 if '*' in str(x) else 0)
df['Runs'] = df['Runs'].replace({'DNB': -1, '0*': 0,'TDNB':-2,'sub':-3,'absent':-4})
df['Runs'] = (df['Runs'].str.replace('*', ''))
df['Runs'] = df['Runs'].fillna(-1).astype(int)
#print(df)
columns_to_replace = ['Mins', 'BF', '4s', '6s', 'SR']
for column in columns_to_replace:
    df[column] = df[column].replace('-', -1)
for i in range(len(df)):
    if df.iloc[i]['Runs'] != -1 and df.iloc[i]['Mins'] == -1:
        df.at[i, 'Mins'] = 0
df = df[df['Player'].notna() & df['Player'].str.strip().astype(bool)]


df = df[df['Runs'] >= 0]
df['Start Date'] = pd.to_datetime(df['Start Date'], infer_datetime_format=True, dayfirst=True)
players_with_more_than_5_innings = df.groupby('Player').filter(lambda x: len(x) > 20)
players_with_more_than_5_innings = players_with_more_than_5_innings.sort_values(by=['Player', 'Start Date'])
df=players_with_more_than_5_innings
print(df)

df.to_csv("Preprocessed dataset.csv")
