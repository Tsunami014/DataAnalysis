# Data analysis
A cool project

This is a flask web application which *currently* can show **some** rainfall and temperature data from the Australian Bureau of Meteorology from a lot of their different weather stations.

The goal for this project is to make a program that can predict the temperature and rainfall for a certain place

## Video demonstration

https://github.com/Tsunami014/DataAnalysis/raw/main/Data%20Analysis%20demo.mp4
</video>

## If something doesn't work
 - ***JEEZ*** TensorFlow SUCKS **<u>SO MUCH</u>**. Sorry for any extra pain. If some code errors on a line that includes the words `import` and `tensorflow` then please feel free to curse and swear at your computer because I have no clue how to fix that other than googling for ages trying multiple things then giving up just as something you *already* tried starts working. Once it took me half an hour to get something working. Hopefully that was just me being bad and you have a better time tho.
 - If you cannot connect to the ftp site it may be because there's something funky on Windows where some security setting blocks the request. If that's an issue, try looking it up.

## TODOS
 - [ ] Find the TOS for the FTP and API
 - [ ] Get data for EVERY place
 - [ ] Get more data (cloud coverage, maybe?)
 - [x] Build the neural network
 - [ ] Make a neural network for rainfall and minimum temperature data
 - [ ] Make NN predict a *slightly* more jagged line if possible (maybe by adjusting how many outputs it does at a tiem: e.g. instead of 30 in and 1 out, have 30 in and 7 out?)
 - [ ] Make sliders to adjust things for the neural network
 - [x] Animate the ... on the loading panel
 - [ ] Add a lot more of the spinning ...'s everywhere
 - [ ] Round the edges of all the plots
 - [ ] Rename 'store files' to 'File downloading and cleaning' to be more precise and clear
 - [x] **ERROR HANDLING**
 - [x] Show where *you* are currently on the map
 - [ ] Show where you are getting the data from on the map
 - [ ] Fix a *small* bug where the place it gets weather from is your current location instead of the actual location the AI is predicting from
