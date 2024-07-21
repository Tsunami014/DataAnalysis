import flask, json
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

@wrapper
def long_task(update):
    import time, random
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking', 'Preparing', 'Cleaning']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast', 'red', 'quick', 'silly']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit', 'fire brigade', 'space station']
    message = ''
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        update(current=i,
               total=total,
               status=message)
        time.sleep(random.randint(2, 20)/10)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}

@app.route('/status/<task_id>')
def status(task_id):
    if task_id not in statuses:
        return flask.jsonify({'State': 'NONEXISTANT'})
    return flask.jsonify(statuses[task_id])

@app.route('/longtask', methods=['POST'])
def longfunc():
    long_task('longtask')
    return flask.jsonify({}), 202

@app.route('/read-form', methods=['POST'])
def read_form(): # Thanks to https://www.geeksforgeeks.org/how-to-use-web-forms-in-a-flask-application/
    # Get the form data as Python ImmutableDict datatype
    data = flask.request.form
  
    ## Return the extracted information
    return data

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
            files['Xtracted'] = resp
            break
    files['Stations'] = xtracted[2]
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

@app.route('/get_files', methods=['POST'])
def get_files(): # Thanks to https://www.geeksforgeeks.org/how-to-use-web-forms-in-a-flask-application/
    global files
    # Get the form data as Python ImmutableDict datatype
    data = {'Cache': 'off', 'Force': 'off'} # Because when it's off, for some reason it does not show in the dict
    data.update(dict(flask.request.form))
    
    get_files_long('get_files', data['Cache'] == 'on', data['Force'] == 'on')
  
    ## Return to the main page
    return flask.redirect('/')

@app.route('/cache_status')
def cache_status():
    return cached_status(flask.request.args.get('cache') == 'true', flask.request.args.get('force') == 'true')

@app.route('/delete_cache')
def delete_cache():
    remove_cache()
    return flask.jsonify({})

@app.route('/get_names')
def get_names():
    # Stored as {'StationNumber': 'Name', ...}
    return flask.jsonify({'Temps': {i: files['Temps'][1](int(i))['Name']+f'({i})' for i in files['Temps'][0]}, 'Rain': files['Rain'][1]})

@app.route('/plot_name_map')
def plot_name_map():
    from numpy import pi, tan, log
    from bokeh.plotting import figure
    from bokeh.models import ColumnDataSource, HoverTool
    locs = getAllNames(files['Xtracted'][1], files['Stations'])
    # range bounds supplied in web mercator coordinates
    xoff, yoff = 12750000, -6250000
    p = figure(x_range=(xoff, 4000000+xoff), y_range=(yoff, 6000000+yoff),
            x_axis_type="mercator", y_axis_type="mercator")

    # Thanks to https://stackoverflow.com/questions/57051517/cant-plot-dots-over-tile-on-bokeh !!!
    k = 6378137
    locs['x'] = locs['Long'] * (k * pi/180.0)
    locs['y'] = log(tan((90 + locs['Lat']) * pi/360.0)) * k

    source = ColumnDataSource(locs)

    p.scatter('x', 'y', source=source, size=5, fill_color="blue", fill_alpha=0.8)

    # Add hover tool
    hover = HoverTool(tooltips=[("Location number", "@Location"), ("Name", "@Name"), ("State", "@State")])
    p.add_tools(hover)

    p.add_tile("CartoDB Positron")

    return json.dumps(json_item(p, "LocationsPlot"))

@app.route('/get_data/<type>/<station>')
def get_data(type, station):
    if type == 'Rain':
        return flask.jsonify(files['Rain'][0][int(station)])
    elif type == 'Temps':
        return flask.jsonify(files['Temps'][0][station])
    else:
        return flask.jsonify({'ERROR': 'Invalid type'}), 404

@app.route('/plot/<type>/<station>')
def plot(type, station):
    from bokeh.plotting import figure
    if type == 'Rain':
        dat = files['Rain'][0][int(station)]
        p = figure(title=f"Rainfall in {files['Rain'][1][int(station)]} ({station})", x_axis_label='Date', x_axis_type="datetime", y_axis_label='Rainfall (mm)')
        p.line(dat['Date'], dat['Rainfall'], legend_label="Rainfall (mm)", line_width=2, line_color="blue")
    elif type == 'Temps':
        dat = files['Temps'][0][station]
        p = figure(title=f"Temperatures in {files['Temps'][1](int(station))['Name']}, {files['Temps'][1](int(station))['State']} ({station})", x_axis_label='Date', x_axis_type="datetime", y_axis_label='Temperature (°C)')
        p.line(dat['Date'], dat['MaxTemp'], legend_label="Max Temp (°C)", line_width=2, line_color="red")
        p.line(dat['Date'], dat['MinTemp'], legend_label="Min Temp (°C)", line_width=2, line_color="blue")
    else:
        return flask.jsonify({'ERROR': 'Invalid type'}), 404
    
    return json.dumps(json_item(p, "myplot"))

@app.route('/')
def main():
    return flask.render_template("index.html", files=str('get_files' in statuses).lower())

app.run()
