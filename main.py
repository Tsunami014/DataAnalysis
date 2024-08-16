from math import ceil
import os
from unittest import result
import flask, json, pickle
from asyncro import wrapper, statuses
from bokeh.embed import json_item
from getWeather import (
    cached_status, 
    remove_cache, 
    getFiles, 
    extractFiles, 
    CleanTemperatures, 
    CleanRainfall, 
    getAllNames
)

app = flask.Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return flask.url_for('static', filename='favicon.ico')

files = {}

@app.route('/status/<task_id>')
def status(task_id):
    if task_id not in statuses:
        return flask.jsonify({'State': 'NONEXISTANT'})
    return flask.jsonify(statuses[task_id])

@app.route('/quicksave/upload')
def uploadData():
    if not os.path.exists('theory/cache/savestate.pkl'):
        return flask.jsonify({'ERROR': 'No quick-save found!'}), 404
    global files, statuses
    with open('theory/cache/savestate.pkl', 'rb') as f:
        files = pickle.loads(f.read())
    statuses['get_data'] = {"State": 'FINISHED', 'txt': 'Successfully loaded quick-save!'}
    ## Return to the main page
    return flask.redirect('/')

@app.route('/quicksave/download')
def downloadData():
    if files == {}:
        return flask.jsonify({'ERROR': 'No data to save!'}), 404
    with open('theory/cache/savestate.pkl', 'wb+') as f:
        pickle.dump(files, f)
    return flask.jsonify({})

@wrapper
def get_files_long(update, cache, force):
    global files
    newfs = None
    for resp, ret in getFiles(cache, force):
        if not ret:
            update(txt=resp)
        else:
            newfs = resp
            break
    xtracted = None
    for resp, ret in extractFiles(newfs):
        if not ret:
            update(txt=resp)
        else:
            xtracted = resp
            break
    files['Names'] = getAllNames(xtracted[1].extractfile('HQDR_stations.txt').read().decode(), xtracted[2])
    for resp, ret in CleanTemperatures(xtracted[0], xtracted[2]):
        if not ret:
            update(txt=resp)
        else:
            files['Temps'] = resp
            break
    for resp, ret in CleanRainfall(xtracted[1]):
        if not ret:
            update(txt=resp)
        else:
            files['Rain'] = resp
            break

@app.route('/stations/get_data', methods=['POST'])
def get_data(): # Thanks to https://www.geeksforgeeks.org/how-to-use-web-forms-in-a-flask-application/
    # Get the form data as Python ImmutableDict datatype
    data = {'Cache': 'off', 'Force': 'off'} # Because when it's off, for some reason it does not show in the dict
    data.update(dict(flask.request.form))
    
    get_files_long('get_data', data['Cache'] == 'on', data['Force'] == 'on')
  
    ## Return to the main page
    return flask.redirect('/')

@app.route('/cache')
def cache_status():
    return cached_status(flask.request.args.get('cache') == 'true', flask.request.args.get('force') == 'true')

@app.route('/cache/delete')
def delete_cache():
    remove_cache()
    return flask.jsonify({})

def names():
    locs = files['Names'].copy()
    def tryName(id):
        try:
            idx = list(locs.Location).index(int(id))
            info = locs.loc[idx]
        except:
            return f'??? ({"0"*(6-len(str(id)))+str(id)})'
        return f'{info["Name"]}{", "+info["State"] if info["State"] != "Unknown" else ""} ({"0"*(6-len(str(id)))+str(id)})'
    # Stored as {'StationNumber': 'Name', ...}
    return {'Temps': {'0'*(6-len(str(i)))+str(i): 'Temp_'+tryName(i) for i in files['Temps']}, 
            'Rain': {'0'*(6-len(str(i)))+str(i): 'Rain_'+tryName(i) for i in files['Rain'][1]}}

@app.route('/stations')
def get_names():
    return flask.jsonify(names())

@app.route('/stations/plot')
def plot_name_map():
    from numpy import pi, tan, log
    from bokeh.plotting import figure
    from bokeh.models import ColumnDataSource, HoverTool
    nms = names()
    places = {i: [int(j) for j in nms[i]] for i in nms}
    placesl = []
    for i in places:
        placesl.extend(places[i])
    locs = files['Names'].copy()
    locs["LocationStr"] = locs["Location"].apply(lambda x: '0'*(6-len(str(x)))+str(x))
    # So we can see what data is available for the places
    locs["Avaliable"] = locs["Location"].apply(lambda x: " & ".join([i for i in [("Temp" if x in places["Temps"] else ""), ("Rain" if x in places["Rain"] else "")] if i]))
    
    # range bounds supplied in web mercator coordinates
    xoff, yoff = 12750000, -6250000
    p = figure(x_range=(xoff, 4000000+xoff), y_range=(yoff, 6000000+yoff),
            x_axis_type="mercator", y_axis_type="mercator", title="Locations of weather stations")

    # Thanks to https://stackoverflow.com/questions/57051517/cant-plot-dots-over-tile-on-bokeh !!!
    k = 6378137
    locs['x'] = locs['Long'] * (k * pi/180.0)
    locs['y'] = log(tan((90 + locs['Lat']) * pi/360.0)) * k

    p.scatter('x', 'y', source=ColumnDataSource(locs[locs["Avaliable"]=="Temp & Rain"]), size=10, fill_color="yellow", fill_alpha=0.9)
    p.scatter('x', 'y', source=ColumnDataSource(locs[locs["Avaliable"]=="Rain"]), size=8, fill_color="blue", fill_alpha=0.7)
    p.scatter('x', 'y', source=ColumnDataSource(locs[locs["Avaliable"]=="Temp"]), size=8, fill_color="red", fill_alpha=0.7)
    p.scatter('x', 'y', source=ColumnDataSource(locs[locs["Avaliable"]==""]), size=4, fill_color="white", fill_alpha=0.5)

    # Add hover tool
    hover = HoverTool(tooltips=[("Location number", "@LocationStr"), ("Name", "@Name"), ("State", "@State"), ("Avaliable data", "@Avaliable")])
    p.add_tools(hover)

    p.add_tile("CartoDB Positron")

    return json.dumps(json_item(p, "LocationsPlot"))

@app.route('/stations/plot/<type>/<station>')
def plot(type, station):
    from bokeh.plotting import figure
    nms = names()
    if type == 'Rain':
        dat = files['Rain'][0][int(station)]
        p = figure(title="Rainfall in "+nms['Rain'][station][5:], x_axis_label='Date', x_axis_type="datetime", y_axis_label='Rainfall (mm)')
        p.line(dat['Date'], dat['Rainfall'], legend_label="Rainfall (mm)", line_width=2, line_color="blue")
    elif type == 'Temps':
        dat = files['Temps']['0'*(6-len(station))+station]
        p = figure(title="Temperatures in "+nms['Temps'][station][5:], x_axis_label='Date', x_axis_type="datetime", y_axis_label='Temperature (°C)')
        p.line(dat['Date'], dat['MaxTemp'], legend_label="Max Temp (°C)", line_width=2, line_color="red")
        p.line(dat['Date'], dat['MinTemp'], legend_label="Min Temp (°C)", line_width=2, line_color="blue")
    else:
        return flask.jsonify({'ERROR': 'Invalid type'}), 404
    
    return json.dumps(json_item(p, "myplot"))

@app.route('/AI/train')
def train_AI():
    train_AI_long('train_AI')
    return flask.jsonify({}), 202

@wrapper
def train_AI_long(update):
    update(txt="Starting AI training...", section=True)
    from time import sleep
    sleep(1)
    for i in range(10):
        update(txt=f"Training AI... {i*10}%", section=False)
        sleep(1)
    return {"txt": "AI trained!", "section": True}

@app.route('/AI/plot')
def plot_AI():
    from bokeh.plotting import figure, Row
    size = {"width": 400, "height": 400}
    ls = figure(title="Losses", x_axis_label='epochs', y_axis_label='losses', **size)
    ls.line([1, 2, 3, 4, 5], [0.1, 0.03, 0.001, 0.0003, 0.00004], line_width=2)
    acc = figure(title="Accuracy", x_axis_label='days', y_axis_label='accuracy', **size)
    acc.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], line_width=2)
    res = figure(title="Results", x_axis_label='days', y_axis_label='results', **size)
    res.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], line_width=2)
    return json.dumps({"INFO": json_item(Row(ls, acc, res, spacing=10), "AIInfo"),
                       "PREDICTIONS": {"text": "The weather will be.........<br><b>SUNNY!!!</b>"}})

@app.route('/')
def main():
    return flask.render_template("index.html", 
                                 files=str('get_data' in statuses).lower(), 
                                 is_disabled=('disabled' if not os.path.exists('theory/cache/savestate.pkl') else '')
                                )

app.run()
