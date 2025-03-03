import pandas as pd

data = pd.read_csv('Preprocessed dataset.csv') 

player_ids = {}
id_counter = 1

# Iterate through the DataFrame and assign IDs
for index, row in data.iterrows():
    player_name = row['Player']
    if player_name not in player_ids:
        player_ids[player_name] = id_counter
        id_counter += 1
    data.loc[index, 'player_id'] = player_ids[player_name]

data['innings_id'] = data.groupby('player_id').cumcount() + 1

data = data.loc[:, ~data.columns.str.contains('^Unnamed')]

data['cumulative_runs'] = data.groupby('player_id')['Runs'].cumsum()
data['cumulative_4s'] = data.groupby('player_id')['4s'].cumsum()
data['cumulative_6s'] = data.groupby('player_id')['6s'].cumsum()
data['cumulative_balls']=data.groupby('player_id')['BF'].cumsum()
data['innings_count'] = data.groupby('player_id').cumcount() + 1 
data['out_innings'] = data.groupby('player_id').apply(lambda x: (x['Not Out'] == 0).cumsum()).reset_index(drop=True)
data['rolling_avg_runs'] = data['cumulative_runs'] / data['out_innings'].replace(0, pd.NA)  
data['rolling_avg_runs'].fillna(0, inplace=True)  
#data['rolling_strike_rate'] = ((data['cumulative_runs'].astype(float) / data['cumulative_balls'].replace(0, pd.NA).astype(float)) * 100).round(decimals=4)
data['rolling_strike_rate'] = (data['cumulative_runs'] / data['cumulative_balls'])*100
#data['peak_performance'] = data.groupby('Player').apply(lambda x: calculate_peak_performance(x)).reset_index(level=0, drop=True)
data['BASRA']=(data['rolling_avg_runs']+data['rolling_strike_rate'])

'''data['previous_avg'] = data['rolling_avg_runs'].shift(1)  
data['previous_strike_rate'] = data['rolling_strike_rate'].shift(1) 
data['previous_avg'].fillna(0, inplace=True)  
data['previous_strike_rate'].fillna(0, inplace=True)'''  

data = data.round(decimals=4)

data.to_csv("Final Dataset.csv", index=False)

print(data)
