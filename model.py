import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

data = pd.read_csv('Final Dataset.csv')

def mark_peak_periods(data, window=7):
    data['is_peak_period'] = 0  
    for player_id in data['player_id'].unique():
        player_data = data[data['player_id'] == player_id]
        player_data['rolling_basra'] = player_data['BASRA'].rolling(window=window).mean()
        peak_start_index = player_data['rolling_basra'].idxmax()  
        if pd.notna(peak_start_index): 
            data.loc[peak_start_index, 'is_peak_period'] = 1  
    return data


data = mark_peak_periods(data)


features = ['cumulative_runs', 'cumulative_4s', 'cumulative_6s', 'cumulative_balls', 
            'rolling_avg_runs', 'rolling_strike_rate', 'BASRA']
target = 'is_peak_period'


scaler = MinMaxScaler()
data[features] = scaler.fit_transform(data[features])

data.sort_values(by=['player_id', 'innings_id'], inplace=True)

def create_sequences(data, features, target, sequence_length=7):
    X, y = [], []
    player_ids = data['player_id'].unique()
    
    for player_id in player_ids:
        player_data = data[data['player_id'] == player_id]
        feature_values = player_data[features].values
        target_values = player_data[target].values
        
        # Create rolling sequences for the model
        for i in range(len(feature_values) - sequence_length + 1):
            X.append(feature_values[i:i+sequence_length])
            y.append(target_values[i+sequence_length-1])  # Predict if last inning in window starts peak
            
    return np.array(X), np.array(y)

X, y = create_sequences(data, features, target)

model = Sequential([
    LSTM(64, activation='relu', input_shape=(X.shape[1], X.shape[2])),
    Dropout(0.2),
    Dense(32, activation='relu'),
    Dense(1, activation='sigmoid')  # Binary output (1 = peak start, 0 = non-peak)
])

model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])

model.fit(X, y, epochs=20, batch_size=16, validation_split=0.2, verbose=1)

def predict_peak_period(new_player_data, features, model, scaler, sequence_length=7, threshold=0.1):
    new_player_data[features] = scaler.transform(new_player_data[features])
    X_new = []

    feature_values = new_player_data[features].values
    basra_values = new_player_data['BASRA'].values  
    innings_ids = new_player_data['innings_id'].values  
    
    for i in range(len(feature_values) - sequence_length + 1):
        X_new.append(feature_values[i:i+sequence_length])
        
    X_new = np.array(X_new)
    
    predictions = model.predict(X_new)
    peak_innings_indices = np.where(predictions.flatten() >= threshold)[0]  
    
    peak_sequences = []
    for idx in peak_innings_indices:
        peak_inning_id = innings_ids[idx + sequence_length - 1]
        peak_basra_sequence = basra_values[idx: idx + sequence_length]
        peak_sequences.append((peak_inning_id, peak_basra_sequence))
    
    if peak_sequences:
        for inning_id, basra_seq in peak_sequences:
            print(f"Predicted peak start at inning {inning_id}")
    else:
        print("No predicted peak performance periods for this player at the current threshold.")
    
    return peak_sequences



new_player_data = pd.read_csv('Ayush Badoni.csv')
predicted_peak_sequences = predict_peak_period(new_player_data, features, model, scaler)

