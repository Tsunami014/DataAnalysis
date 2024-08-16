# Get savestate
from pickle import load
with open('theory/cache/savestate.pkl', 'rb') as f:
    files = load(f)

import matplotlib.pyplot as plt
from random import randint
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