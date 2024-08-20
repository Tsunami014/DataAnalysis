# phase3-1.py optimized for import
import ftplib, io, os, re, shutil
import zipfile, tarfile
import openmeteo_requests
import requests_cache
import geocoder
import pandas as pd
from unlzw3 import unlzw
from retry_requests import retry
from io import StringIO

pd.options.mode.chained_assignment = None  # default='warn'
# It gives a warning which I can do nothing about, so I must stop it warning me

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
    yield "Cleaning Temperature data (may take a short while)...", False
    # 41 = len('v2.4-raw-data-and-supporting-information/')
    dirs = [i for i in tmps.namelist() if i[41:].startswith('raw-data/') if i[41:] not in ['raw-data/Raw data.7z', 'raw-data/']]
    datas = [tmps.open(i).read().decode() for i in dirs]

    def clean_data(dat):
        cleaned = re.sub(' +', ',', # Replace the spaces that *were* the deliminers to commas. Theer were not the same number of spaces each time either.
                        re.sub('\r?\n......', '\n', dat) # Remove the station number and \r. The station number is the same every time, and returned along with the dataframe.
        ).replace(',\n', '\n' # Because the spaces are a pain and all over the place!
                            )[6:] # The first station number does not get cleaned, so remove it here. 
        df = pd.read_csv(StringIO('Date,MaxTemp,MinTemp\n'+cleaned))
        df = df.drop(df[(df.MaxTemp == -999) | (df.MinTemp == -999)].index) # Remove all missing data coz it's useless
        df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d') # Turn the dates into **real** dates!
        df['MaxTemp'] = df['MaxTemp']/10 # Adjust the temperature because of how it was stored
        df['MinTemp'] = df['MinTemp']/10 # Adjust the temperature because of how it was stored
        return df.to_dict('list')

    yield {i[:6]: clean_data(i) for i in datas}, True

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

def getAllNames(nms, nms2):
    spl = [(int(i[:8]), i[8:12].strip(), i[12:18].strip(), i[18:59].strip(), i[59:75].strip(), float(i[75:84]), float(i[84:])) for i in nms2.split('\n') if i != '']
    names = ["Location", "State", "???", "Name", "????", "Lat", "Long"]
    locs = pd.DataFrame({names[j]: {str(i): spl[i][j] for i in range(len(spl))} for j in range(len(names))})#'Location,State,???,Name,????,Lat,Long\n'+z)
    # Until I find what it is, I'll remove the unknown columns
    locs = locs.drop(columns=['???', '????'])

    locs2 = pd.read_csv(StringIO("Location,Lat,Long,Elevation,Name\n"+re.sub('^(.*?) (.*?) (.*?) (.*?) (.*)', r'\1,\2,\3,\4,\5', nms, flags=re.M)))
    locs2 = locs2.drop('Elevation', axis=1) # Don't need the elevation; and also isn't in the other dataset
    locs2['State'] = "Unknown"
    locs = pd.concat((locs, locs2))
    locs = locs.drop_duplicates(['Location'], keep='first') # First still has state data
    locs.reset_index(drop=True, inplace=True)
    return locs

# phase3-3.ipynb but each cell is it's own function for importing

def getMyLocation():
    g = geocoder.ip('me')
    return g.latlng

def getCurrentWeather():
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('./theory/cache/', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    lat, lng = getMyLocation()
    params = {
        "latitude": round(lat, 2),
        "longitude": round(lng, 2),
        "hourly": "temperature_2m",
        "timezone": "Australia/Sydney",
        "past_days": 92,
        "models": "bom_access_global"
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    hourly_data["temperature_2m"] = hourly_temperature_2m

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    return hourly_dataframe

def cleanweather(weatherdf):
    newdf = weatherdf[weatherdf.apply(lambda row: row.date.hour==0, axis=1)]
    return newdf.reset_index().drop('index', axis=1)
