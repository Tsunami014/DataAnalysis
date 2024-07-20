# phase3-1.py optimized for import

import ftplib, io, os, re, shutil
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

def isCached():
    return {i: os.path.exists('./theory/cache/'+i) for i in files.keys()}

def remove_cache():
    shutil.rmtree('./theory/cache')
    os.mkdir('./theory/cache')

def cached_status(cache=True, force=False):
    allcached = isCached()
    cacheds = ([] if force else [i for i in allcached if allcached[i]])
    fullyCached = len(cacheds) == len(allcached)
    return ('<b>Force redownloading all cached</b>' if force else (
    f'Fully cached all {len(allcached)} file{"s" if len(allcached) != 1 else ""}' if fullyCached else (
        f'{len(cacheds)} file{"s" if len(cacheds) != 1 else ""} cached out of {len(allcached)}' if len(cacheds) > 0 else 'Not cached'
)))+f". Will download {str(len(allcached)-len(cacheds))} file{'s' if len(allcached)-len(cacheds) != 1 else ''} and will {'<i><u>not</u></i> ' if not cache else ''}cache them once downloaded.\n"

def getFiles(cache=True, force=False):
    allcached = isCached()
    cacheds = ([] if (not cache) or force else [i for i in allcached if allcached[i]])
    fullyCached = len(cacheds) == len(allcached)
    if fullyCached:
        yield "Cache has all the files! Using them.", False
        yield {i: i for i in cacheds}, True
    fs = {}
    yield "Connecting to ftp server...", False
    server = ftplib.FTP()
    server.connect("134.178.253.145") # Also known as ftp.bom.gov.au
    yield "Logging in...", False
    server.login()
    for i in files:
        if i in cacheds:
            yield f"Using cached file '{i}'...", False
            fs[i] = i
            continue
        yield f"Downloading file '{i}' at ftp://ftp.bom.gov.au{files[i]} (may take a while)...", False
        newf = io.BytesIO()
        server.retrbinary('RETR '+files[i], newf.write)
        fs[i] = newf
        if cache:
            yield f"Caching file '{i}'...", False
            with open(f'./theory/cache/{i}', 'wb') as f:
                f.write(newf.getvalue())
    yield "Quitting server connection...", False
    server.quit()
    yield fs, True

def extractFiles(fs):
    extracted = []
    for i in fs:
        if i.endswith('.txt'):
            yield f"Opening text file '{i}'...", False
            if isinstance(fs[i], str):
                extracted.append(open(f'./theory/cache/{fs[i]}').read())
            else:
                extracted.append(fs[i].getvalue().decode())
            continue
        typ = 'tar' if i.endswith('.tar') else 'zip'
        if isinstance(fs[i], str):
            yield f"Extracting cached {typ} file '{i}'...", False
            fs[i] = f'./theory/cache/{fs[i]}'
        else:
            yield f"Extracting downloaded {typ} file '{i}'...", False
        if i.endswith('.tar'):
            if isinstance(fs[i], str):
                extracted.append(tarfile.open(fs[i]))
            else:
                extracted.append(tarfile.open(fileobj=fs[i]))
        else:
            extracted.append(zipfile.ZipFile(fs[i]))
    yield extracted, True

def CleanTemperatures(tmps, nms):
    yield "Cleaning Names...", False
    spl = [(int(i[:8]), i[8:12].strip(), i[12:18].strip(), i[18:59].strip(), i[59:75].strip(), float(i[75:84]), float(i[84:])) for i in nms.split('\n') if i != '']
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
    
    yield "Cleaning Temperature data (may take a short while)...", False
    dirs = [i for i in tmps.namelist() if i.startswith('raw-data/') if i != 'raw-data/Raw data.7z' and i != 'raw-data/']
    datas = [tmps.open(i).read().decode() for i in dirs]

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
        return df.to_dict('list')

    yield [{i[:6]: clean_data(i) for i in datas}, getInfo], True

def CleanRainfall(rfs):
    dirs = rfs.getnames()
    dirs.remove('HQDR_stations.txt')
    datas = {}
    j = 0
    for i in dirs:
        j += 1
        yield f"\rUnzipping files (Will be a while)... {j} / {len(dirs)}", False
        datas[i] = unlzw(rfs.extractfile(i).read()).decode()
    yield "Done!", False

    def clean_data(dat):
        # Info is stored as: "????         StationNumber DateFrom DateTo missing_value=MISSINGVALUE Name\r\n"
        info = dat[:dat.index("\r")-1][4:].strip().split(' ')
        cleaned = re.sub(' +', ',', # Replace the spaces that *were* the deliminers to commas.
                        dat[dat.index("\n")+1:].replace('\r\n', '\n') # Make the newlines consistent
        )
        df = pd.read_csv(StringIO('Date,Rainfall\n'+cleaned))
        df = df.drop(df[df.Rainfall == float(info[3][14:])].index) # Remove all missing data coz it's useless
        df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d') # Turn the dates into **real** dates!
        return df.to_dict('list'), {"Station": int(info[0]), "Name": " ".join(info[4:])}

    yield "Cleaning Rainfall data (may take a short while)...", False
    cleanDatas = {}
    stationMap = {}
    for i in datas:
        df, info = clean_data(datas[i])
        cleanDatas[info['Station']] = df
        stationMap[info['Station']] = info['Name']
    yield [cleanDatas, stationMap], True
