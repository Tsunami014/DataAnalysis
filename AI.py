import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from threading import Thread
from io import StringIO
from contextlib import redirect_stdout
from random import randint
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator

class AI:
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.model = None
        self.length = None
    
    def train(self, data, batch_size=3, length=30):
        """
        _summary_

        Parameters
        ----------
        data : _type_
            _description_
        batch_size : int, optional
            "Number of timeseries samples in each batch", by default 20
            Also can be known as 'how many runs will occur at the same time'.
            If you have a powerful computer, turn this up. If not, maybe turn this down a bit.
        length : int, optional
            Length of the output sequences (in number of timesteps), by default 30
        """
        scaled_full_data = self.scaler.fit_transform(data)
        self.length = length
        generator = TimeseriesGenerator(scaled_full_data, scaled_full_data, length=length, batch_size=batch_size)
        # Create the model
        self.model = Sequential([
            LSTM(length, input_shape=(length, 1)),
            Dense(1)
        ])
        self.model.compile(optimizer='adam', loss='mse')
        self.model.fit(generator,epochs=6)
    
    @property
    def losses(self):
        return pd.DataFrame(self.model.history.history)

    def predict(self, data, amount_into_future, actual=None):
        current_batch = self.scaler.fit_transform(data).reshape((1, self.length, 1))
        forecast = []
        closenesses = []
        for i in range(amount_into_future):
            # get prediction 1 time stamp ahead ([0] is for grabbing just the number instead of [array])
            current_pred = self.model.predict(current_batch)[0]
            
            unscaled_pred = self.scaler.inverse_transform(current_pred.reshape(-1,1))[0]
            # store prediction
            forecast.append(unscaled_pred)
            if actual is not None:
                # Add how close it is to the list
                closenesses.append(abs(unscaled_pred - actual[i]))
            # update batch to now include prediction and drop first value
            current_batch = np.append(current_batch[:,1:,:],[[current_pred]],axis=1)
        return forecast, closenesses

def runAIonData(tempdf, update):
    s = StringIO()
    done = False
    def runWhile():
        from time import sleep
        while not done:
            update(txt=s.getvalue())
            sleep(0.5)
    t = Thread(target=runWhile, daemon=True)
    t.start()
    with redirect_stdout(s):
        graphs = {}
        df = pd.DataFrame(data=tempdf['MaxTemp'],columns=['Temp'])
        # Split training and testing data
        test_amount = 7
        test_window = 1000
        train_amount = len(df)-test_window

        train = df.iloc[:train_amount]

        ai = AI()

        ai.train(train, batch_size=20, length=30)
        ai.model.summary()

        graphs['losses'] = ai.losses

        offset = randint(0, test_window)
        test = df.iloc[-test_amount-30-offset:-offset-test_amount].Temp.to_numpy().reshape(-1, 1)
        real = df.iloc[-offset-test_amount:-offset].Temp.to_numpy().reshape(-1, 1)

        forecast, closenesses = ai.predict(test, test_amount, real)

        graphs['initial'] = test
        graphs['forecast'] = list(test[-1])+[i[0] for i in forecast]
        graphs['real'] = np.append(test[-1],real)

        graphs['closenesses'] = closenesses
    done = True
    
    return graphs