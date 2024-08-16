import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pickle import load
from random import randint
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator

# Get savestate
with open('theory/cache/savestate.pkl', 'rb') as f:
    files = load(f)

while True:
    place = files['Names'].loc[randint(0, len(files['Names']))]
    if '0'*(6-len(str(place.Location)))+str(place.Location) in files['Temps']:
        break
# place = '27042'

tempdf = files['Temps']['0'*(6-len(str(place.Location)))+str(place.Location)]
plt.plot(tempdf['Date'], tempdf['MaxTemp'], label='Max Temp', color="red", alpha=0.7)
plt.plot(tempdf['Date'], tempdf['MinTemp'], label='Min Temp', color="blue", alpha=0.7)
plt.legend()
#plt.fill_between(df['Date'], df['MaxTemp'], df['MinTemp'], alpha=0.3)
plt.xlabel('Date')
plt.ylabel('Temperature (°C)')
plt.title(f'Temperature in {place.Name} ({place.Location}) over time.')
plt.show()
# PLEASE NOTE: If there is a gap, it is because there is no data for that time. This is not an error.

df = pd.DataFrame(data=tempdf['MaxTemp'],columns=['Temp'])


# Split training and testing data
test_amount = 7
test_window = 1000
train_amount = len(df)-test_window

# define generator
batch_size = 20 # Number of timeseries samples in each batch
length = 30 # Length of the output sequences (in number of timesteps)

train = df.iloc[:train_amount]

# Scale data
scaler = MinMaxScaler()
scaled_full_data = scaler.fit_transform(train)
generator = TimeseriesGenerator(scaled_full_data, scaled_full_data, length=length, batch_size=batch_size)
# What does the first batch look like?
X,y = generator[0]
print(f'Given the Array: \n{X.flatten()}')
print(f'Predict this y: \n {y}')

# Create the model
n_features = 1
model = Sequential([
    LSTM(length, input_shape=(length, n_features)),
    Dense(1)
])
model.compile(optimizer='adam', loss='mse')
model.fit(generator,epochs=6)

model.summary()

losses = pd.DataFrame(model.history.history)
losses.plot()

first_eval_batch = scaled_full_data[-length:]
first_eval_batch.reshape((1, length, n_features))

offset = randint(0, test_window)
test = df.iloc[-test_amount-length-offset:-offset]
scaled_test_data = scaler.fit_transform(test)

forecast = []
closenesses = []

first_eval_batch = scaled_test_data[:length]
current_batch = first_eval_batch.reshape((1, length, n_features))

tot = len(test)
for i in range(tot-length):
    # get prediction 1 time stamp ahead ([0] is for grabbing just the number instead of [array])
    current_pred = model.predict(current_batch)[0]
    
    unscaled_pred = scaler.inverse_transform(current_pred.reshape(-1,1))[0]
    # store prediction
    forecast.append(unscaled_pred)
    # Add how close it is to the list
    closenesses.append(abs(unscaled_pred - test.iloc[length+i]))
    # update batch to now include prediction and drop first value
    current_batch = np.append(current_batch[:,1:,:],[[current_pred]],axis=1)

initial = first_eval_batch
plt.plot(scaler.inverse_transform(initial), 'r-', label='Input')
x_axis = range(len(initial)-1, len(initial)+len(test)-length)
plt.plot(x_axis, list(scaler.inverse_transform(initial[-1].reshape(1, -1))[0])+[i[0] for i in forecast], 'b-', label='Predicted')
plt.plot(x_axis, np.append(scaler.inverse_transform(initial[-1].reshape(1, -1))[0],scaler.inverse_transform(scaled_test_data[length:])), '--', color='orange', label='Actual')
plt.legend()
plt.ylim(ymin=0)
plt.show()

plt.plot(closenesses, 'b-')
plt.show()