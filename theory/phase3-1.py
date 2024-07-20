# A port of phase3-1.ipynb to Python

import ftplib, io, os, re
import zipfile, tarfile
import pandas as pd
import matplotlib.pyplot as plt
from unlzw3 import unlzw
from io import StringIO
from random import randint

files = {
    'temps.zip': '/anon/home/ncc/www/change/ACORN_SAT_daily/v2.4-raw-data-and-supporting-information.zip',
    'rain.tar': '/anon/home/ncc/www/change/HQdailyR/HQ_daily_prcp_txt.tar',
    'stations.txt': '/anon/gen/clim_data/IDCKWCDEA0/tables/stations_db.txt'
}

if not os.getcwd().endswith('/theory'):
    os.chdir(os.getcwd()+'/theory')

def isCached():
    return {i: os.path.exists('./cache/'+i) for i in files.keys()}

# Checking the cache
allcached = isCached()
cache = input("Do you want to cache files for faster loads but taking up more space? (y/n)> ").lower() != 'n'
force = input("Do you want to force redownload the files from the internet regardless of if they're cached? (y/n)> ").lower() == 'y'
cacheds = ([] if (not cache) or force else [i for i in allcached if allcached[i]])
fullyCached = len(cacheds) == len(allcached)
print("Caching status: "+('Force redownloading all cached' if force else (
    f'Fully cached all {len(allcached)} file{"s" if len(allcached) != 1 else ""}' if fullyCached else (
        f'{len(cacheds)} file{"s" if len(cacheds) != 1 else ""} cached out of {len(allcached)}' if len(cacheds) > 0 else 'Not cached'
)))+f". Will download {str(len(allcached)-len(cacheds))} file{'s' if len(allcached)-len(cacheds) != 1 else ''} and will {'not ' if not cache else ''}cache them once downloaded.\n")

def getFiles():
    if fullyCached:
        print("Cache has all the files! Using them.")
        return {i: i for i in cacheds}
    fs = {}
    print("Connecting to ftp server...")
    server = ftplib.FTP()
    server.connect("134.178.253.145") # Also known as ftp.bom.gov.au
    print("Logging in...")
    server.login()
    for i in files:
        if i in cacheds:
            print(f"Using cached file '{i}'...")
            fs[i] = i
            continue
        print(f"Downloading file '{i}' at ftp://ftp.bom.gov.au{files[i]} (may take a while)...")
        newf = io.BytesIO()
        server.retrbinary('RETR '+files[i], newf.write)
        fs[i] = newf
        if cache:
            print(f"Caching file '{i}'...")
            with open(f'./cache/{i}', 'wb') as f:
                f.write(newf.getvalue())
    print("Quitting server connection...")
    server.quit()
    return fs

def extractFiles(fs):
    extracted = []
    for i in fs:
        if i.endswith('.txt'):
            print(f"Opening text file '{i}'...")
            if isinstance(fs[i], str):
                extracted.append(open(f'./cache/{fs[i]}').read())
            else:
                extracted.append(fs[i].getvalue().decode())
            continue
        typ = 'tar' if i.endswith('.tar') else 'zip'
        if isinstance(fs[i], str):
            print(f"Extracting cached {typ} file '{i}'...")
            fs[i] = f'./cache/{fs[i]}'
        else:
            print(f"Extracting downloaded {typ} file '{i}'...")
        if i.endswith('.tar'):
            if isinstance(fs[i], str):
                extracted.append(tarfile.open(fs[i]))
            else:
                extracted.append(tarfile.open(fileobj=fs[i]))
        else:
            extracted.append(zipfile.ZipFile(fs[i]))
    return extracted

fs = getFiles()
print("All files collected! Extracting...")
xtracteds = extractFiles(fs)

print("All files extracted!!! :)")

z = xtracteds[2]
spl = [(int(i[:8]), i[8:12].strip(), i[12:18].strip(), i[18:59].strip(), i[59:75].strip(), float(i[75:84]), float(i[84:])) for i in z.split('\n') if i != '']
names = ["Location", "State", "???", "Name", "????", "Lat", "Long"]
locs = pd.DataFrame({names[j]: {str(i): spl[i][j] for i in range(len(spl))} for j in range(len(names))})#'Location,State,???,Name,????,Lat,Long\n'+z)
# Until I find what it is, I'll remove the unknown columns
locs = locs.drop(columns=['???', '????'])

def getInfo(id):
    part = locs[locs['Location'] == id]
    if len(part) == 0:
        return {
        'Name': 'Unknown', 
        'State': 'Unknown', 
        'Lat': 'Unknown', 
        'Long': 'Unknown'
    }
    return {
        'Name': part.Name.values[0], 
        'State': part.State.values[0], 
        'Lat': part.Lat.values[0], 
        'Long': part.Long.values[0]
    }

z = xtracteds[0]
dirs = [i for i in z.namelist() if i.startswith('raw-data/') if i != 'raw-data/Raw data.7z' and i != 'raw-data/']
datas = [z.open(i).read().decode() for i in dirs]

def clean_data(dat):
    cleaned = re.sub(' +', ',', # Replace the spaces that *were* the deliminers to commas. Theer were not the same number of spaces each time either.
                     re.sub('\r\n......', '\n', dat) # Remove the station number and \r. The station number is the same every time, and returned along with the dataframe.
    ).replace(',\n', '\n' # Because the spaces are a pain and all over the place!
                         )[6:] # The first station number does not get cleaned, so remove it here. 
    df = pd.read_csv(StringIO('Date,MaxTemp,MinTemp\n'+cleaned))
    df = df.drop(df[(df.MaxTemp == -999) | (df.MinTemp == -999)].index) # Remove all missing data coz it's useless
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d') # Turn the dates into **real** dates!
    df['MaxTemp'] = df['MaxTemp']/10 # Adjust the temperature because of how it was stored
    df['MinTemp'] = df['MinTemp']/10 # Adjust the temperature because of how it was stored
    return df

print('Cleaning data (may take a short while)...')
alls = {i[:6]: clean_data(i) for i in datas}
print('Done!')

place = list(alls.keys())[randint(0, len(alls)-1)]
# place = '27042'
df = alls[place]
plt.plot(df['Date'], df['MaxTemp'], label='Max Temp', color="red", alpha=0.7)
plt.plot(df['Date'], df['MinTemp'], label='Min Temp', color="blue", alpha=0.7)
plt.legend()
#plt.fill_between(df['Date'], df['MaxTemp'], df['MinTemp'], alpha=0.3)
plt.xlabel('Date')
plt.ylabel('Temperature (°C)')
plt.title(f'Temperature in {getInfo(int(place))["Name"]} ({place}) over time.')
plt.show()

z = xtracteds[1]
dirs = z.getnames()
dirs.remove('HQDR_stations.txt')
print()
datas = {}
j = 0
for i in dirs:
    j += 1
    print(f"\rUnzipping files (Will be a while)... {j} / {len(dirs)}", end="")
    datas[i] = unlzw(z.extractfile(i).read()).decode()
print("\nDone!")

def clean_data(dat):
    # Info is stored as: "????         StationNumber DateFrom DateTo missing_value=MISSINGVALUE Name\r\n"
    info = dat[:dat.index("\r")-1][4:].strip().split(' ')
    cleaned = re.sub(' +', ',', # Replace the spaces that *were* the deliminers to commas.
                     dat[dat.index("\n")+1:].replace('\r\n', '\n') # Make the newlines consistent
    )
    df = pd.read_csv(StringIO('Date,Rainfall\n'+cleaned))
    df = df.drop(df[df.Rainfall == float(info[3][14:])].index) # Remove all missing data coz it's useless
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d') # Turn the dates into **real** dates!
    return df, {"Station": int(info[0]), "Name": " ".join(info[4:])}

print("Cleaning Rainfall data (may take a short while)...")
cleanDatas = {}
stationMap = {}
for i in datas:
    df, info = clean_data(datas[i])
    cleanDatas[info['Station']] = df
    stationMap[info['Station']] = info['Name']
print("Done!")

place = list(cleanDatas.keys())[randint(0, len(cleanDatas)-1)]
# place = '27042'
df = cleanDatas[place]
plt.plot(df['Date'], df['Rainfall'], color="blue", alpha=0.9)
plt.xlabel('Date')
plt.ylabel('Rainfall (mm)') # At least, I'm *assuming* it's in mm
plt.title(f'Rainfall in {stationMap[place]} ({place}) over time.')
plt.show()
