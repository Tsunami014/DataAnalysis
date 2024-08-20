# Phase 1: Identifying and Defining
- > Choose Your Data Scenario: You'll be working with different data scenarios such as weather data, bushfire
data, or solar power data. Pick one that interests you the most.

    The data I want to analyze is the weather data. This includes temperature and rainfall data from different places all over Australia. The goal for this is to be able to use it to train a neural network to predict the weather (temperature and rainfall) for a certain place; providing the user with the answer to, 'Will it rain?'. I will be getting data from the [Australian Bureau of Meteorology](http://www.bom.gov.au); from their FTP site (ftp://ftp.bom.gov.au) which will provide detailed historical data and [their API](https://open-meteo.com/en/docs) to provide data to compare the AI's response with (or maybe get extra data). All this data is publicly avaliable without the need for an API key or registration or anything.
- > Specify Requirements: List down the functional (what your project should do) and non-functional
(qualities like speed or security) requirements for your project. Be specific.

    - Functional requirements:
        - Data loading: The data should be loaded and processed correctly, with all errors handled correctly and returned back to the user so they can fix it. The user will press a button and it will output constantly the progress it's making on the downloading/cleaning process.
        - Data cleaning: The system should remove all unknown data and process the data so only the required columns are needed to make it easier to use and store. This will all be done after you press a button and then it will automatically download everything then cleans it all, constantly reporting back on it's progress.
        - Data analysis: The system needs to allow for getting the data to graph it but also getting a range of data to train and test the neural network with. This will be done by the user selecting a dataset to train the AI with and then pressing the start button and it will start training in the background, reporting on it's progress until it finishes; then it will output some cool graphs on it's training accuracy and stuff and it's current weather prediction for that selected data, in addition to the prediction by the BOM as well.
        - Data visualisation: The data will be visualised with [Bokeh](https://bokeh.org/), so users can interact with the graph and also because it is easier to implement in Flask and less hacky than Matplotlib. The visualisation will be line graphs and a map; line graphs for the weather data and predictions to show the trends in the data and a map to show the locations of where the data is avaliable for. The map will display automatically when it detects the data exists, but the graphs for the individual places will only show if you have selected that place in a dropdown; making it easy to select specific data to view.
        - Data storage: The data will be cached once downloaded, and once again once cleaned. This is so users can not only still have access to the data offline if they cached it already but also improve speeds; making you not have to wait for it to get/clean the files every time you want to use the program again. The after downloaded will be stored as their file types that were in the original FTP site, which is a .txt, .zip and .tar file. The cleaned data will be stored as a .pkl file which contains a pickled representation of the list of all the cleaned data and their dataframes. This will work by the user selecting options for caching the downloaded files; an option to cache them once downloaded and one to force redownload if you want to. There will also be a download and upload button to save the cleaned data.
        - API: The program should be able to be called by an API service to provide more applications of this product. The API should be easily accessable, and should be RESTful.
    - Non-Functional:
        - Asthetics: The program needs to look good so people can have a nice time using the product
        - Speed: The program should be fast in order to provide the user with a better interface and quick response.
        - Accuracy: The program should be able to provide the user with a correct range of temperature and chance of rain; so the user can plan their day accordingly.
        - Usability: The program should be easy to setup, install and use to allow for users to have a good time using it and also so they *can* in the first place.
- > Use Cases: Provide an example of how users will interact with the system.

    - ```yaml
      Actor: User
      Goal: To download the files needed.
      Preconditions: User either has all the files already cached in the folder OR has a wifi connection that allows reading the BOM FTP.
      Main Flow:
       - FOR each file:
           - IF file is already cached AND NOT force redownloading:
               - System gets file from cache.
           - ELSE:
               - System connects to the FTP site if not already
               - System tells user it's downloading file
               - System downloads file from predetermined location
      Postconditions: All files are successfully downloaded
      After:
       - System moves on to cleaning (see below)
      ```
    - ```yaml
      Actor: System
      Goal: To clean the data and get only the things needed
      Preconditions: The user has downloaded the files
      Main Flow:
       - FOR (temperature,rainfall):
           - Unzip the data into an object
           - Find all the raw data files in the zip
           - Turn them into pandas dataframes and clean them
      Postconditions: Cleaned data is stored in a dictionary
      After:
       - System saves cleaned data as a pickled python object
       - System plots the data in the UI
      ```
    - ```yaml
      Actor: User
      Goal: To display the cleaned data about a place
      Preconditions: The user has the cleaned information stored and has selected a place
      Main Flow:
       - System loads the data into a graph
       - System passes the graph data to the UI and the UI displays the graph
      Postconditions: None
      After: Nothing happens
      ```
    - ```yaml
      Actor: User
      Goal: To train a neural network to predict the weather for a place
      Preconditions: The user has the cleaned information stored and has selected a place
      Main Flow:
       - Get the data avaliable for the place specified
       - Feed it into the neural network
       - Start it's training
       - Report on the training progression regularly
      Postconditions: Model has finished it's training
      After:
       - Show cool graphs on training
       - Show the model's prediction of the weather
       - Let user save model for ease of use again
      ```
